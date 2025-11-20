#!/bin/bash

source ~/super-secret-password-file

BASEDIR=$(dirname "$0")
echo "$BASEDIR"
/usr/bin/python "$BASEDIR/message_senders.py" 'shutdown starting'
~/code/github/bh-observatory/operations/monitoring/allsky_camera/all_sky.sh > all_sky.log 2>&1
indi_setprop "Atik 383L+ CCD.CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE"=0 && sleep 300

#echo "Performing light frame calibration"
#cd ~/code/github/bh-observatory/data-reduction/calibration
#python calibrateLightFrames.py
sleep 300
echo 'Powering off PC'
sleep 10
systemctl poweroff
