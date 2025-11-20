#!/bin/bash

# Grabs a screenshot and uploads to the cloud. Used to monitor activity.
# NOTE: For this to run in cron, you  need to do  'xhost si:localuser:root' as non root
# See https://superuser.com/questions/1721539/terminal-in-xrdp-session-solve-authorization-required-but-no-authorization-pr

export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
gnome-screenshot --display=:0 -f ~/Pictures/screenshot.png


scp ~/Pictures/screenshot.png dokeeffe@52-8.xyz:/var/www/html/images/telemetry/.
rm ~/Pictures/screenshot.png
