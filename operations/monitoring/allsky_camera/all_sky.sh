#!/bin/bash

cd "$(dirname "$0")"
export ZWO_ASI_LIB=/opt/asi/lib/x64/libASICamera2.so
mkdir -p ~/Pictures/allsky
if [[ $(indi_getprop | grep Roof.STATE) =~ "OPEN" ]] 
then
    python all_sky.py
else
    python all_sky_day.py
fi
cp ~/Pictures/allsky/allsky.jpg ~/Pictures/allsky/allsky_$(date +%F_%H-%M).jpg
scp ~/Pictures/allsky/allsky.jpg dokeeffe@52-8.xyz:/var/www/html/images/.
