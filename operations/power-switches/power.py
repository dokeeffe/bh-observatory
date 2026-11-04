#!/usr/bin/env python3
"""Interactive Textual UI to control TP-Link Kasa plugs and strip outlets.

Requires: pip install python-kasa textual
"""
import asyncio
import sys

from kasa import Discover
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Input, Label, Static

# Outlets (by alias) that need a confirmation before being switched OFF.
# Matching is case-insensitive.
DANGEROUS_OFF = {"main pc"}


async def update_device(device):
    try:
        await device.update()
        return None
    except Exception as e:  # noqa: BLE001
        return f"Could not update {device.alias}: {e}"


async def load_outlets():
    """Discover all Kasa devices and return their switchable outlets."""
    try:
        devices = await Discover.discover(discovery_timeout=10)
    except Exception as e:  # noqa: BLE001
        return [], [f"Discovery failed: {e}"]

    ordered_devices = sorted(devices.values(), key=lambda device: device.host)
    update_errors = await asyncio.gather(
        *(update_device(device) for device in ordered_devices)
    )
    outlets = []
    for dev in ordered_devices:
        if dev.children:
            outlets.extend(dev.children)
        else:
            outlets.append(dev)
    return outlets, [error for error in update_errors if error]


async def set_state(outlet, turn_on):
    if turn_on:
        await outlet.turn_on()
    else:
        await outlet.turn_off()
    await outlet.update()


async def refresh(outlets):
    """Update each device once; refreshing a strip also updates its outlets."""
    seen = set()
    errors = []
    for outlet in outlets:
        target = getattr(outlet, "parent", None) or outlet
        if id(target) in seen:
            continue
        seen.add(id(target))
        try:
            await target.update()
        except Exception as e:  # noqa: BLE001
            errors.append(f"Refresh failed for {target.alias}: {e}")
    return errors


class ConfirmPowerOff(ModalScreen[bool]):
    """Require the user to type an outlet name before powering it off."""

    CSS = """
    ConfirmPowerOff {
        align: center middle;
    }

    #confirm-dialog {
        width: 68;
        height: auto;
        padding: 1 2;
        border: round $warning;
        background: $surface;
    }

    #confirm-dialog Input {
        margin: 1 0;
    }

    #confirm-buttons {
        align-horizontal: right;
        height: auto;
    }
    """

    def __init__(self, alias):
        super().__init__()
        self.alias = alias

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-dialog"):
            yield Label(f"⚠ '{self.alias}' may be the machine running this script.")
            yield Label("Turning it off will immediately cut its power.")
            yield Label(f"Type {self.alias!r} to confirm:")
            yield Input(placeholder=self.alias, id="confirmation")
            with Horizontal(id="confirm-buttons"):
                yield Button("Cancel", id="cancel")
                yield Button("Power off", variant="error", id="confirm")

    def on_mount(self) -> None:
        self.query_one("#confirmation", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            value = self.query_one("#confirmation", Input).value
            self.dismiss(value.casefold() == self.alias.casefold())
        else:
            self.dismiss(False)


class PowerApp(App):
    TITLE = "Kasa Power Switches"
    CSS = """
    Screen {
        background: $background;
    }

    #intro {
        padding: 1 2 0 2;
        color: $text-muted;
    }

    #outlets {
        height: 1fr;
        padding: 0 1;
    }

    .outlet-row {
        height: 5;
        padding: 1 2;
        margin: 0 0 1 0;
        border: round $primary-darken-2;
        background: $surface;
        align: left middle;
    }

    .outlet-row.selected {
        border: round $accent;
    }

    .outlet-name {
        width: 1fr;
        content-align: left middle;
        text-style: bold;
    }

    .state {
        width: 12;
        content-align: center middle;
        text-style: bold;
    }

    .state.on {
        color: $success;
    }

    .state.off {
        color: $error;
    }

    .outlet-row Button {
        margin-left: 1;
    }

    #status {
        height: 2;
        padding: 0 2;
        color: $text-muted;
    }
    """
    BINDINGS = [
        ("up", "previous_outlet", "Previous outlet"),
        ("down", "next_outlet", "Next outlet"),
        ("left", "turn_selected_off", "Off"),
        ("right", "turn_selected_on", "On"),
        ("enter", "toggle_selected", "Toggle"),
        ("space", "toggle_selected", "Toggle"),
        ("r", "refresh", "Refresh"),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(
            "Controls: ↑/↓ select outlet · ← turn off · → turn on · "
                "Enter/Space toggle · click a button · R rescan · Q quit",
            id="intro",
        )
        yield VerticalScroll(id="outlets")
        yield Static("", id="status")
        yield Footer()

    async def on_mount(self) -> None:
        self.outlets = []
        self._busy = False
        self.selected_index = 0
        self.set_interval(5, self._start_periodic_refresh)
        self.set_interval(30, self._start_periodic_discovery)
        await self._discover()

    async def _discover(self) -> None:
        await self._load_devices()

    async def _load_devices(self) -> None:
        self._set_status("Discovering Kasa switches on the network...")
        outlets, errors = await load_outlets()
        self.outlets = outlets
        self.selected_index = 0
        container = self.query_one("#outlets", VerticalScroll)
        await container.remove_children()
        if self.outlets:
            for index, outlet in enumerate(self.outlets):
                await container.mount(self._make_row(index, outlet))
        else:
            await container.mount(Static("No Kasa switches found.", classes="empty"))
        self._render_states()
        if errors:
            self._set_status("; ".join(errors))
        elif self.outlets:
            self._set_status(f"Found {len(self.outlets)} switch outlet(s)")
        else:
            self._set_status("No Kasa switches found")

    def _make_row(self, index, outlet) -> Horizontal:
        return Horizontal(
            Label(outlet.alias, classes="outlet-name"),
            Static("", id=f"state-{index}", classes="state"),
            Button("⏻ Toggle", id=f"toggle-{index}", variant="primary"),
            Button("🟢 On", id=f"on-{index}", variant="success"),
            Button("🔴 Off", id=f"off-{index}", variant="error"),
            id=f"outlet-{index}",
            classes="outlet-row",
        )

    def _render_states(self) -> None:
        for index, outlet in enumerate(self.outlets):
            row = self.query_one(f"#outlet-{index}", Horizontal)
            row.set_class(index == self.selected_index, "selected")
            state = self.query_one(f"#state-{index}", Static)
            if outlet.is_on:
                state.update("🟢 ON")
                state.set_classes("state on")
            else:
                state.update("🔴 OFF")
                state.set_classes("state off")

    def _set_status(self, message) -> None:
        self.query_one("#status", Static).update(message)

    def _start_periodic_refresh(self) -> None:
        if self.outlets and not self._busy:
            self.run_worker(
                self.refresh_outlets(),
                group="device-refresh",
                exclusive=True,
            )

    def _start_periodic_discovery(self) -> None:
        if not self._busy:
            self.run_worker(
                self.discover_outlets(),
                group="device-discovery",
                exclusive=True,
            )

    async def discover_outlets(self) -> None:
        if self._busy:
            return
        self._busy = True
        try:
            await self._load_devices()
        finally:
            self._busy = False

    async def refresh_outlets(self) -> None:
        if self._busy or not self.outlets:
            return
        self._busy = True
        try:
            errors = await refresh(self.outlets)
            self._render_states()
            self._set_status("; ".join(errors) if errors else "State refreshed")
        finally:
            self._busy = False

    async def action_refresh(self) -> None:
        await self.discover_outlets()

    def _move_selection(self, amount) -> None:
        if not self.outlets:
            return
        self.selected_index = (self.selected_index + amount) % len(self.outlets)
        self._render_states()
        self.query_one(f"#outlet-{self.selected_index}", Horizontal).scroll_visible()

    def action_previous_outlet(self) -> None:
        self._move_selection(-1)

    def action_next_outlet(self) -> None:
        self._move_selection(1)

    async def action_turn_selected_off(self) -> None:
        await self._set_outlet_state(self.selected_index, False)

    async def action_turn_selected_on(self) -> None:
        await self._set_outlet_state(self.selected_index, True)

    async def action_toggle_selected(self) -> None:
        if self.outlets:
            outlet = self.outlets[self.selected_index]
            await self._set_outlet_state(self.selected_index, not outlet.is_on)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        try:
            action, index_text = button_id.rsplit("-", 1)
            index = int(index_text)
        except ValueError:
            return
        if action not in {"toggle", "on", "off"} or self._busy:
            return

        self.selected_index = index
        turn_on = not self.outlets[index].is_on if action == "toggle" else action == "on"
        await self._set_outlet_state(index, turn_on)

    async def _set_outlet_state(self, index, turn_on) -> None:
        if self._busy or not self.outlets:
            return
        outlet = self.outlets[index]
        if not turn_on and outlet.alias.casefold() in DANGEROUS_OFF:
            confirmed = await self.push_screen_wait(ConfirmPowerOff(outlet.alias))
            if not confirmed:
                self._set_status("Power-off cancelled")
                return

        self._busy = True
        self._set_status(f"Switching {outlet.alias} {'on' if turn_on else 'off'}...")
        try:
            await set_state(outlet, turn_on)
            self._render_states()
            self._set_status(f"{outlet.alias} is {'ON' if outlet.is_on else 'OFF'}")
        except Exception as e:  # noqa: BLE001
            self._set_status(f"Failed to switch {outlet.alias}: {e}")
        finally:
            self._busy = False


if __name__ == "__main__":
    try:
        PowerApp().run()
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)
