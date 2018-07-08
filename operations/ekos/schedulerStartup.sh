#!/bin/bash
BASEDIR=$(dirname "$0")
echo "$BASEDIR"

/usr/bin/python "$BASEDIR/message_senders.py" startup
echo 'Switching OFF IR Lamps'
curl 'http://192.168.1.222/decoder_control.cgi?command=94' -H 'Authorization: Basic YWRtaW46enhjdmJuMw=='
echo 'Switching OFF Dehumidifier'
/usr/bin/python "$BASEDIR/tplink_hs1xx/smartplug.py" dehumidifier OFF
# set ccd cooler on
#indi_setprop "Atik 383L+ CCD.CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE"=-20
# Check park status of roof and scope, check xml files

# Check weather


