#!/bin/bash

#
# Start indi services if not started, use weather station as test connection. If not started then we need to also power on all equipment first.
#
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo $DIR

echo 'Powering on equipment'
$DIR/python/firmataSwitcher.py /dev/arduino_AL01C9VU 2
sleep 10

CONNECTED=$((indi_eval -f '"Indi Cloud Rain Monitor.CONNECTION.CONNECT"==1') 2>&1)
if [[ $CONNECTED == "connect: Connection refused" ]]
then
    echo 'starting indi services'
    nohup sh $DIR/startIndiServer.sh &
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
#    exit 1
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
# Weather status must be ok if we get here. Proceed to open roof
# Connect to the roof and open. REAL DATA (16deg outside and -1.5 from the sky. Actually about 80/90% clear) Needs a recalculation
# -2.4 +13deg was 100% clear
# -0.7 +16deg was 85/95% clear
# -2 +14 totally clear I think (remote)
# -1 +16 totally clear I think (remote)
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

#
# Wake the telescope from hibernation
#
echo 'waking telescope'
$DIR/nexstarPoweronAndWake.sh 


#
# Disconnect any indi drivers used
#
indi_setprop 'Aldi Roof.CONNECTION.CONNECT=Off'
indi_setprop 'Indi Cloud Rain Monitor.CONNECTION.CONNECT=On'

echo 'Waiting for Telescope GPS to lock'
sleep 120
echo 'Startup procedure complete'
