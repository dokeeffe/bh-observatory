#!/bin/bash
DEHUMIDIFIER=192.168.2.229
BASEDIR=$(dirname "$0")
echo "$BASEDIR"

/usr/bin/python "$BASEDIR/message_senders.py" startup
echo 'Switching OFF IR Lamps'
curl 'http://192.168.2.220/decoder_control.cgi?command=94' -H 'Authorization: Basic ZG9rZWVmZmU6ZG9rZWVmZmU='
echo 'Switching OFF Dehumidifier'
/usr/bin/python "$BASEDIR/tplink_hs1xx/smartplug.py" $DEHUMIDIFIER OFF
# set ccd cooler on
indi_setprop "Atik 383L+ CCD.CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE"=-20
# Check park status of roof and scope, check xml files

# Check weather


