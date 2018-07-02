#!/bin/bash
DEHUMIDIFIER=192.168.1.229
BASEDIR=$(dirname "$0")
echo "$BASEDIR"
/usr/bin/python "$BASEDIR/message_senders.py" 'WATCHDOG starting shutdown'
indi_setprop "Atik 383L+ CCD.CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE"=0
sleep 300
curl http://192.168.1.225:8080/power/ccd/off > /dev/null 2>&1
curl http://192.168.1.225:8080/power/filterwheel/off > /dev/null 2>&1
curl http://192.168.1.225:8080/power/mount/off > /dev/null 2>&1
curl http://192.168.1.225:8080/power/heaters/off > /dev/null 2>&1
curl http://192.168.1.225:8080/power/focuser/off > /dev/null 2>&1
curl http://192.168.1.225:8080/power/aux/off > /dev/null 2>&1
echo 'Switching ON IR Lamps'
curl 'http://192.168.1.222/decoder_control.cgi?command=95' -H 'Authorization: Basic ZG9rZWVmZmU6ZG9rZWVmZmU=' > /dev/null 2>&1
echo 'Switching ON Dehumidifier'
/usr/bin/python "$BASEDIR/tplink_hs1xx/smartplug.py" $DEHUMIDIFIER ON

/usr/bin/python "$BASEDIR/message_senders.py" 'shutdown complete'
sleep 10
systemctl poweroff
