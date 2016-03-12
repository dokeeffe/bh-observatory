#!/bin/bash
echo 'Aborting equipment motion'
CONNECTED=$((indi_eval -f '"Aldi roof.CONNECTION.CONNECT"==1') 2>&1)
echo $CONNECTED
if [ $CONNECTED -eq 0 ]
then
    echo 'Connecting roof driver'
    indi_setprop 'Aldi roof.CONNECTION.CONNECT=On'
    sleep 10
fi
indi_setprop 'Aldi roof.DOME_MOTION.DOME_CW=Off'
indi_setprop 'Aldi roof.DOME_MOTION.DOME_CCW=Off'
indi_setprop 'Aldi roof.DOME_ABORT_MOTION.ABORT=On'

