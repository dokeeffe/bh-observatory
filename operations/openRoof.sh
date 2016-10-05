#!/bin/bash
echo 'Opening Roof'
echo 'Opening Roof'
CONNECTED=$((indi_eval -f '"Aldi Roof.CONNECTION.CONNECT"==1') 2>&1)
echo $CONNECTED
if [ $CONNECTED -eq 0 ]
then
    echo 'Connecting Roof driver'
    indi_setprop 'Aldi Roof.CONNECTION.CONNECT=On'
    sleep 10
fi
indi_setprop 'Aldi Roof.DOME_MOTION.DOME_CCW=Off'
indi_setprop 'Aldi Roof.DOME_MOTION.DOME_CW=On'
