#!/bin/bash

set -o pipefail

# Replace 'dokeeffe' with your actual username if different
KSTARS_PID=$(pgrep -u dokeeffe kstars | head -1)

if [ -z "$KSTARS_PID" ]; then
    echo "KStars is not running" >> /tmp/ekos-cron.log
    exit 1
fi

export DBUS_SESSION_BUS_ADDRESS=$(grep -z DBUS_SESSION_BUS_ADDRESS "/proc/$KSTARS_PID/environ" | cut -d= -f2-)

if [ -z "$DBUS_SESSION_BUS_ADDRESS" ]; then
    echo "Could not find DBus session address" >> /tmp/ekos-cron.log
    exit 1
fi

fetch_dbus_string() {
    /usr/bin/gdbus call \
        --session \
        --dest org.kde.kstars \
        --object-path /KStars/Ekos/Scheduler \
        --method "org.kde.kstars.Ekos.Scheduler.$1" |
        /usr/bin/python3 -c '
import ast
import sys

result = ast.literal_eval(sys.stdin.read())
if not isinstance(result, tuple) or len(result) != 1 or not isinstance(result[0], str):
    raise SystemExit("Unexpected DBus return value")
sys.stdout.write(result[0])
sys.stdout.write("\n")
'
}

# Grab ekos data and save
JSON_TMP=$(mktemp /tmp/ekos.json.XXXXXX) || exit 1
LOG_TMP=$(mktemp /tmp/ekos_log.txt.XXXXXX) || {
    rm -f "$JSON_TMP"
    exit 1
}
trap 'rm -f "$JSON_TMP" "$LOG_TMP"' EXIT

if ! fetch_dbus_string jsonJobs > "$JSON_TMP"; then
    echo "Failed to fetch Ekos scheduler jobs over DBus" >> /tmp/ekos-cron.log
    exit 1
fi

if ! fetch_dbus_string logText > "$LOG_TMP"; then
    echo "Failed to fetch Ekos scheduler log over DBus" >> /tmp/ekos-cron.log
    exit 1
fi

mv "$JSON_TMP" /tmp/ekos.json
mv "$LOG_TMP" /tmp/ekos_log.txt
