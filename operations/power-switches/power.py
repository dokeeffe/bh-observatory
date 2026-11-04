#!/usr/bin/env python3
"""Interactive CLI to switch TP-Link Kasa plugs / strip outlets on and off.

Requires: pip install python-kasa
"""
import asyncio
import sys

from kasa import Discover

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
        return dev
    except Exception as e:  # noqa: BLE001
        print(f"  ! Could not reach {host}: {e}")
        return None


async def load_outlets():
    """Return a flat list of switchable things: strip children and single plugs."""
    devices = await asyncio.gather(*(connect(h) for h in HOSTS))
    outlets = []
    for dev in devices:
        if dev is None:
            continue
        if dev.children:
            for child in dev.children:
                outlets.append(child)
        else:
            outlets.append(dev)
    return outlets


def show(outlets):
    print()
    for i, o in enumerate(outlets, 1):
        state = "ON " if o.is_on else "OFF"
        print(f"  {i}. [{state}] {o.alias}")
    print()
    print("  Enter a number to toggle, 'on N' / 'off N' to set explicitly,")
    print("  'r' to refresh, 'q' to quit.")


def confirm_power_off(alias):
    print()
    print("  " + "!" * 60)
    print(f"  WARNING: '{alias}' is probably the machine running this script.")
    print("  Switching it OFF will cut power to it immediately (hard power-off).")
    print("  " + "!" * 60)
    answer = input(f"  Type the outlet name ({alias}) to confirm: ").strip()
    return answer.lower() == alias.lower()


async def set_state(outlet, turn_on):
    if turn_on:
        await outlet.turn_on()
    else:
        await outlet.turn_off()
    await outlet.update()
    print(f"  -> {outlet.alias} is now {'ON' if outlet.is_on else 'OFF'}")


async def refresh(outlets):
    # Updating the parent refreshes its children; update each unique parent once.
    seen = set()
    for o in outlets:
        target = getattr(o, "parent", None) or o
        if id(target) in seen:
            continue
        seen.add(id(target))
        try:
            await target.update()
        except Exception as e:  # noqa: BLE001
            print(f"  ! Refresh failed for {target.alias}: {e}")


async def main():
    print("Discovering devices...")
    outlets = await load_outlets()
    if not outlets:
        print("No devices found.")
        return 1

    loop = asyncio.get_running_loop()

    while True:
        show(outlets)
        raw = (await loop.run_in_executor(None, input, "> ")).strip().lower()
        if not raw:
            continue
        if raw in ("q", "quit", "exit"):
            return 0
        if raw in ("r", "refresh"):
            await refresh(outlets)
            continue

        parts = raw.split()
        explicit = None
        if parts[0] in ("on", "off") and len(parts) == 2:
            explicit = parts[0] == "on"
            idx_str = parts[1]
        elif len(parts) == 1:
            idx_str = parts[0]
        else:
            print("  ? Didn't understand that.")
            continue

        if not idx_str.isdigit() or not (1 <= int(idx_str) <= len(outlets)):
            print("  ? Pick a number from the list.")
            continue

        outlet = outlets[int(idx_str) - 1]
        turn_on = (not outlet.is_on) if explicit is None else explicit

        if not turn_on and outlet.alias.lower() in DANGEROUS_OFF:
            ok = await loop.run_in_executor(None, confirm_power_off, outlet.alias)
            if not ok:
                print("  Cancelled.")
                continue

        try:
            await set_state(outlet, turn_on)
        except Exception as e:  # noqa: BLE001
            print(f"  ! Failed: {e}")


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except (KeyboardInterrupt, EOFError):
        print()

