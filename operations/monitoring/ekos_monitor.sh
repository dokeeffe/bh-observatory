#!/bin/bash

#!/bin/bash

# Replace 'dokeeffe' with your actual username if different
KSTARS_PID=$(pgrep -u dokeeffe kstars | head -1)

if [ -z "$KSTARS_PID" ]; then
    echo "KStars is not running" >> /tmp/ekos-cron.log
    exit 1
fi

export DBUS_SESSION_BUS_ADDRESS=$(grep -z DBUS_SESSION_BUS_ADDRESS /proc/$KSTARS_PID/environ | cut -d= -f2-)

if [ -z "$DBUS_SESSION_BUS_ADDRESS" ]; then
    echo "Could not find DBus session address" >> /tmp/ekos-cron.log
    exit 1
fi

# Grab ekos data and scp to host
/usr/bin/qdbus org.kde.kstars /KStars/Ekos/Scheduler org.kde.kstars.Ekos.Scheduler.jsonJobs > /tmp/ekos.json && scp /tmp/ekos.json dokeeffe@52-8.xyz:/var/www/html/images/telemetry/.
/usr/bin/qdbus org.kde.kstars /KStars/Ekos/Scheduler org.kde.kstars.Ekos.Scheduler.logText > /tmp/ekos_log.txt && scp /tmp/ekos_log.txt dokeeffe@52-8.xyz:/var/www/html/images/telemetry/.
