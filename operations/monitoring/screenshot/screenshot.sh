#!/bin/bash

export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
gnome-screenshot --display=:0 -f ~/Pictures/screenshot.png
scp ~/Pictures/screenshot.png dokeeffe@52-8.xyz:/var/www/html/images/telemetry/.
rm ~/Pictures/screenshot.png
