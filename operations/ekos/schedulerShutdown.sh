#!/bin/bash
BASEDIR=$(dirname "$0")
echo "$BASEDIR"
/usr/bin/python "$BASEDIR/scheduler_workflow_script.py" shutdown-starting
indi_setprop "Atik 383L+ CCD.CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE"=0
sleep 300
curl http://192.168.2.225:8080/power/ccd/off > /dev/null 2>&1
curl http://192.168.2.225:8080/power/filterwheel/off > /dev/null 2>&1
curl http://192.168.2.225:8080/power/mount/off > /dev/null 2>&1
curl http://192.168.2.225:8080/power/heaters/off > /dev/null 2>&1
curl http://192.168.2.225:8080/power/focuser/off > /dev/null 2>&1
curl http://192.168.2.225:8080/power/aux/off > /dev/null 2>&1
echo 'Switching ON IR Lamps'
curl 'http://192.168.2.220/decoder_control.cgi?command=95' -H 'Authorization: Basic ZG9rZWVmZmU6ZG9rZWVmZmU=' > /dev/null 2>&1
/usr/bin/python "$BASEDIR/scheduler_workflow_script.py" shutdown-complete

