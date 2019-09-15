#!/bin/bash

source ~/super-secret-password-file

BASEDIR=$(dirname "$0")
echo "$BASEDIR"
/usr/bin/python "$BASEDIR/message_senders.py" 'shutdown starting'
~/code/github/bh-observatory/operations/monitoring/allsky_camera/all_sky.sh > all_sky.log 2>&1
indi_setprop "Atik 383L+ CCD.CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE"=0 && sleep 300
curl http://192.168.1.225:8080/power/ccd/off > /dev/null 2>&1
curl http://192.168.1.225:8080/power/filterwheel/off > /dev/null 2>&1
curl http://192.168.1.225:8080/power/mount/off > /dev/null 2>&1
curl http://192.168.1.225:8080/power/heaters/off > /dev/null 2>&1
curl http://192.168.1.225:8080/power/focuser/off > /dev/null 2>&1
curl http://192.168.1.225:8080/power/aux/off > /dev/null 2>&1
echo 'Switching ON IR Lamps'
curl 'http://192.168.1.222/decoder_control.cgi?command=95' -u $INDOOR_FOSCAM_USERNAME:$INDOOR_FOSCAM_PASSWORD > /dev/null 2>&1 || true
curl "http://192.168.1.221:88/cgi-bin/CGIProxy.fcgi?cmd=setInfraLedConfig&mode=0&usr=$OUTDOOR_FOSCAM_USERNAME&pwd=$OUTDOOR_FOSCAM_PASSWORD" || true
echo 'Switching ON Dehumidifier'
/usr/bin/python "$BASEDIR/tplink_hs1xx/smartplug.py" dehumidifier ON

dropbox start
echo "Clearing all landed WCS headers"
find ~/Pictures/Landed/ -name *.fits | xargs delwcs
echo "Performing light frame calibration"
cd ~/code/github/bh-observatory-data/data-reduction/calibration
python calibrateLightFrames.py
cd ~/code/github/bh-observatory-data/data-reduction
echo "updating filenames"
python addFitsObjectToFilename.py
echo "plate solving"
python solveAll.py
/usr/bin/python "$BASEDIR/message_senders.py" 'shutdown and calibration complete'
echo "uploading to dropbox"
find ~/Pictures/CalibratedLight/ -cmin -60 -exec cp {} ~/Dropbox  \;
until dropbox status | grep 'Up to date' -C 9999; do sleep 30; done
echo 'Powering off PC'
sleep 10
systemctl poweroff
