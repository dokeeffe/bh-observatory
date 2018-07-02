#!/bin/bash
DEHUMIDIFIER=192.168.1.229
BASEDIR=$(dirname "$0")
echo "$BASEDIR"

/usr/bin/python "$BASEDIR/message_senders.py" startup
echo 'Switching OFF IR Lamps'
<<<<<<< HEAD
curl 'http://192.168.1.222/decoder_control.cgi?command=94' -H 'Authorization: Basic ZG9rZWVmZmU6ZG9rZWVmZmU='
=======
curl 'http://192.168.1.220/decoder_control.cgi?command=94' -H 'Authorization: Basic ZG9rZWVmZmU6ZG9rZWVmZmU='
>>>>>>> ecd170c4692d5dd7ccf10dd0400204ec4208e70b
echo 'Switching OFF Dehumidifier'
/usr/bin/python "$BASEDIR/tplink_hs1xx/smartplug.py" $DEHUMIDIFIER OFF
# set ccd cooler on
#indi_setprop "Atik 383L+ CCD.CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE"=-20
# Check park status of roof and scope, check xml files

# Check weather


