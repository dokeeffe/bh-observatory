#!/bin/bash

cd "$(dirname "$0")"
export ZWO_ASI_LIB=/opt/asi/lib/x64/libASICamera2.so
mkdir -p ~/Pictures/allsky
if [[ $(indi_getprop | grep Roof.STATE) =~ "OPEN" ]];
then
    echo 'roof open, taking outdoor exp'
    python all_sky.py
else
    echo 'roof closed taking indoor exp'
    python all_sky.py
fi
cp ~/Pictures/allsky/allsky.jpg ~/Pictures/allsky/allsky_$(date +%F_%H-%M).jpg
scp ~/Pictures/allsky/allsky.jpg dokeeffe@52-8.xyz:/var/www/html/images/.
