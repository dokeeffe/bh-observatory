#!/bin/bash

DISPLAY=:0 scrot ~/Pictures/screenshot.png
scp ~/Pictures/screenshot.png dokeeffe@52-8.xyz:/var/www/html/images/telemetry/.
rm ~/Pictures/screenshot.png
