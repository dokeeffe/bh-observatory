#!/bin/bash
echo 'Closing Roof'
CONNECTED=$((indi_eval -f '"Aldi Roof.CONNECTION.CONNECT"==1') 2>&1)
echo $CONNECTED
if [ $CONNECTED -eq 0 ]
then
    echo 'Connecting roof driver'
    indi_setprop 'Aldi Roof.CONNECTION.CONNECT=On'
    sleep 10
fi
mpg123 resources/alarm.mp3
indi_setprop 'Aldi Roof.DOME_MOTION.DOME_CW=On'
indi_setprop 'Aldi Roof.DOME_MOTION.DOME_CCW=Off'

