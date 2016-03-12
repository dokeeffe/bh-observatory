#!/bin/bash

#
# Start indi services if not started, use weather station as test connection
#
CONNECTED=$((indi_eval -f '"Indi Cloud Rain Monitor.CONNECTION.CONNECT"==1') 2>&1)
if [[ $CONNECTED == "connect: Connection refused" ]]
then
    echo 'starting indi services'
    nohup sh startIndiServer.sh &
    sleep 10
    CONNECTED=$((indi_eval -f '"Indi Cloud Rain Monitor.CONNECTION.CONNECT"==1') 2>&1)
fi

#
# Verify weather situation and exit if in warning state
#
if [ $CONNECTED -eq 0 ]
then
    echo 'Connecting weather station driver'
    indi_setprop 'Indi Cloud Rain Monitor.CONNECTION.CONNECT=On'
    sleep 10
fi

CLOUD_ALERT=$((indi_eval -f '"Indi Cloud Rain Monitor.WEATHER_STATUS.WEATHER_CLOUD_COVER"==3') 2>&1)
WEATHER_STATION_ALERT=$((indi_eval -f '"Indi Cloud Rain Monitor.WEATHER_STATUS.WEATHER_STATION_ONLINE"==3') 2>&1)
RAIN_ALERT=$((indi_eval -f '"Indi Cloud Rain Monitor.WEATHER_STATUS.WEATHER_RAIN"==3') 2>&1)
echo '==== WEATHER CONDITIONS ==='
echo 'Weather device = '${WEATHER_STATION_ALERT}
echo 'Rain = '${RAIN_ALERT}
echo 'Cloud = '${CLOUD_ALERT}

if [ $CLOUD_ALERT -eq 1 ]
then
    echo 'Weather cloud param in alert state, exiting'
    exit 1
fi
if [ $RAIN_ALERT -eq 1 ]
then
    echo 'Weather rain param in alert state, exiting'
    exit 1
fi
if [ $WEATHER_STATION_ALERT -eq 1 ]
then
    echo 'Weather station is offline or malfunctioning, exiting'
    exit 1
fi

#
# Weather status must be ok if we get here. Proceed to power on all equipement
#
echo 'Powering on equipment'
./python/firmataSwitcher.py /dev/arduino_AL01C9VU 2

#
# Connect to the roof and open. Make a warning beep beep....
#
echo 'Opening Roof'
CONNECTED=$((indi_eval -f '"Aldi roof.CONNECTION.CONNECT"==1') 2>&1)
echo $CONNECTED
if [ $CONNECTED -eq 0 ]
then
    echo 'Connecting roof driver'
    indi_setprop 'Aldi roof.CONNECTION.CONNECT=On'
    sleep 10
fi
indi_setprop 'Aldi roof.DOME_MOTION.DOME_CCW=Off'
indi_setprop 'Aldi roof.DOME_MOTION.DOME_CW=On'

#
# Wake the telescope from hibernation
#
echo 'waking telescope'
./nexstarPoweronAndWake.sh 

