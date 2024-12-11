#!/bin/bash

~/code/github/simple-allsky-camera/allsky.py
scp ~/Pictures/allsky/"$(ls -t ~/Pictures/allsky | head -1)" dokeeffe@52-8.xyz:/var/www/html/images/telemetry/allsky.jpg


