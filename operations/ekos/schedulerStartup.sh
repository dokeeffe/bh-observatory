#!/bin/bash

echo 'Running scheduler startup script'
source ~/super-secret-password-file

BASEDIR=$(dirname "$0")
echo "$BASEDIR"

#/usr/bin/python "$BASEDIR/message_senders.py" startup
echo 'Switching OFF IR Lamps'
curl 'http://192.168.1.222/decoder_control.cgi?command=94' -u $INDOOR_FOSCAM_USERNAME:$INDOOR_FOSCAM_PASSWORD || true
curl "http://192.168.1.221:88/cgi-bin/CGIProxy.fcgi?cmd=setInfraLedConfig&mode=1&usr=$OUTDOOR_FOSCAM_USERNAME&pwd=$OUTDOOR_FOSCAM_PASSWORD" || true
curl "http://192.168.1.221:88/cgi-bin/CGIProxy.fcgi?cmd=closeInfraLed&usr=$OUTDOOR_FOSCAM_USERNAME&pwd=$OUTDOOR_FOSCAM_PASSWORD" || true


echo 'Switching OFF Dehumidifier'
/usr/bin/python "$BASEDIR/tplink_hs1xx/smartplug.py" dehumidifier OFF || echo "** FAILED to turn off dehumidifier"


