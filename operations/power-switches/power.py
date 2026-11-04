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

# Legacy-protocol devices: no credentials needed.
HOSTS = [
    "192.168.1.23",   # KP303 strip
    "192.168.1.254",  # HS100
    "192.168.1.8",    # KP105
]

# Outlets (by alias) that need a confirmation before being switched OFF.
# Matching is case-insensitive.
DANGEROUS_OFF = {"main pc"}


async def connect(host):
    try:
        dev = await asyncio.wait_for(Discover.discover_single(host), timeout=10)
        await dev.update()
        return dev, None
    except Exception as e:  # noqa: BLE001
        return None, f"Could not reach {host}: {e}"


async def load_outlets():
    """Return discovered outlets and any connection errors."""
    results = await asyncio.gather(*(connect(host) for host in HOSTS))
    outlets = []
    errors = []
    for dev, error in results:
        if error:
            errors.append(error)
        if dev is None:
            continue
        if dev.children:
            outlets.extend(dev.children)
        else:
            outlets.append(dev)
    return outlets, errors


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
        ("r", "refresh", "Refresh"),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Discovering Kasa switches...", id="intro")
        yield VerticalScroll(id="outlets")
        yield Static("", id="status")
        yield Footer()

    async def on_mount(self) -> None:
        self.outlets = []
        self._busy = False
        self.set_interval(5, self._start_periodic_refresh)
        await self._discover()

    async def _discover(self) -> None:
        self._set_status("Discovering switches...")
        self.outlets, errors = await load_outlets()
        container = self.query_one("#outlets", VerticalScroll)
        await container.remove_children()
        if self.outlets:
            for index, outlet in enumerate(self.outlets):
                await container.mount(self._make_row(index, outlet))
        else:
            await container.mount(Static("No Kasa switches found.", classes="empty"))
        self._render_states()
        self._set_status("; ".join(errors) if errors else "Ready")

    def _make_row(self, index, outlet) -> Horizontal:
        return Horizontal(
            Label(outlet.alias, classes="outlet-name"),
            Static("", id=f"state-{index}", classes="state"),
            Button("⏻ Toggle", id=f"toggle-{index}", variant="primary"),
            Button("🟢 On", id=f"on-{index}", variant="success"),
            Button("🔴 Off", id=f"off-{index}", variant="error"),
            classes="outlet-row",
        )

    def _render_states(self) -> None:
        for index, outlet in enumerate(self.outlets):
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
        await self.refresh_outlets()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        try:
            action, index_text = button_id.rsplit("-", 1)
            index = int(index_text)
        except ValueError:
            return
        if action not in {"toggle", "on", "off"} or self._busy:
            return

        outlet = self.outlets[index]
        turn_on = (
            not outlet.is_on if action == "toggle"
            else action == "on"
        )
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
