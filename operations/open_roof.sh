#!/bin/bash

if [[ $(curl --silent http://192.168.2.227:8080/weather/current | jq -r '.rain') = *true* ]]; then
  echo "WEATHER: RAINING. Cannot open roof"
  exit 1
fi
SKYTEMP=$(curl --silent http://192.168.2.227:8080/weather/current | jq -r '.skyTemp' | bc) 
if [ $(echo "$SKYTEMP > -10" | bc) -ne 0 ] 
then 
  echo "WEATHER: CLOUDY:"
fi

echo "Opening roof"
indi_setprop 'Aldi Roof.CONNECTION.CONNECT=Off'
sleep 0.5
indi_setprop 'Aldi Roof.CONNECTION.CONNECT=On'
sleep 2
if [[ $(indi_getprop 'Aldi Roof.STATE.State') = *OPEN* ]]; then
  echo "ROOF ALREADY OPEN"
  exit 1
fi
if [[ $(indi_getprop 'Aldi Roof.STATE.State') = *UNKNOWN* ]]; then
  echo "ROOF STATE UNKNOWN EXITING"
  exit 1
fi
indi_setprop 'Aldi Roof.DOME_PARK.UNPARK=On'
OUTPUT=""; 
while [ `echo $OUTPUT | grep -c OPEN` = 0 ]; do 
  OUTPUT=`indi_getprop 'Aldi Roof.STATE.State'`;
  echo $OUTPUT 
  sleep 0.25
done
indi_setprop 'Aldi Roof.CONNECTION.CONNECT=Off'

