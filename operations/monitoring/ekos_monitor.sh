#!/bin/bash

set -o pipefail

# Replace 'dokeeffe' with your actual username if different
KSTARS_PID=$(pgrep -u dokeeffe kstars | head -1)

if [ -z "$KSTARS_PID" ]; then
    echo "KStars is not running" >> /tmp/ekos-cron.log
    exit 1
fi

export DBUS_SESSION_BUS_ADDRESS=$(
    tr '\0' '\n' < "/proc/$KSTARS_PID/environ" |
        sed -n 's/^DBUS_SESSION_BUS_ADDRESS=//p'
)

if [ -z "$DBUS_SESSION_BUS_ADDRESS" ]; then
    echo "Could not find DBus session address" >> /tmp/ekos-cron.log
    exit 1
fi

fetch_dbus_property() {
    local output
    output=$(
        /usr/bin/gdbus call \
            --session \
            --dest org.kde.kstars \
            --object-path /KStars/Ekos/Scheduler \
            --method org.freedesktop.DBus.Properties.Get \
            org.kde.kstars.Ekos.Scheduler "$1"
    ) || return 1

    printf '%s\n' "$output" |
        /usr/bin/python3 -c '
import ast
import sys

output = sys.stdin.read().strip()
if not output.startswith("(<") or not output.endswith(">,)"):
    raise SystemExit("Unexpected DBus property response")

try:
    value = ast.literal_eval(output[2:-3])
except (SyntaxError, ValueError) as error:
    raise SystemExit(f"Could not parse DBus property response: {error}")

expected_type = sys.argv[1]
if expected_type == "string" and isinstance(value, str):
    sys.stdout.write(value)
    sys.stdout.write("\n")
elif expected_type == "string-list" and isinstance(value, list) and all(
    isinstance(line, str) for line in value
):
    sys.stdout.writelines(f"{line}\n" for line in value)
else:
    raise SystemExit("Unexpected DBus property type")
' "$2"
}

# Grab ekos data and save
JSON_TMP=$(mktemp /tmp/ekos.json.XXXXXX) || exit 1
LOG_TMP=$(mktemp /tmp/ekos_log.txt.XXXXXX) || {
    rm -f "$JSON_TMP"
    exit 1
}
trap 'rm -f "$JSON_TMP" "$LOG_TMP"' EXIT

if ! fetch_dbus_property jsonJobs string > "$JSON_TMP"; then
    echo "Failed to fetch Ekos scheduler jobs over DBus" >> /tmp/ekos-cron.log
    exit 1
fi

if ! fetch_dbus_property logText string-list > "$LOG_TMP"; then
    echo "Failed to fetch Ekos scheduler log over DBus" >> /tmp/ekos-cron.log
    exit 1
fi

mv "$JSON_TMP" /tmp/ekos.json
mv "$LOG_TMP" /tmp/ekos_log.txt
