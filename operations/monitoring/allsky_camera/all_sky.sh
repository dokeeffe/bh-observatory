#!/bin/bash

cd "$(dirname "$0")"
export ZWO_ASI_LIB=/opt/asi/lib/x64/libASICamera2.so
mkdir -p /tmp/allsky
[[ $(indi_getprop | grep Roof.STATE) =~ "OPEN" ]] && python all_sky.py
cp /tmp/allsky.jpg /tmp/allsky/allsky_$(date +%F_%R).jpg
scp /tmp/allsky.jpg dokeeffe@52-8.xyz:/var/www/html/images/.
