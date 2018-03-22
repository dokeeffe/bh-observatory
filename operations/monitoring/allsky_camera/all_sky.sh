#!/bin/bash

cd "$(dirname "$0")"
export ZWO_ASI_LIB=/opt/asi/lib/x64/libASICamera2.so
python all_sky.py
timestamp=`date -u "+%F_%H_%M-%S"`
convert ~/Pictures/allsky/allsky.jpg -fill '#9999' -draw 'rectangle 5,917,203,950' -fill white -pointsize 20 -annotate +10+940 ${timestamp} ~/Pictures/allsky/allsky.jpg
cp ~/Pictures/allsky/allsky.jpg ~/Pictures/allsky/allsky_$(date -u +%F_%H-%M-%S).jpg
scp ~/Pictures/allsky/allsky.jpg dokeeffe@52-8.xyz:/var/www/html/images/.
