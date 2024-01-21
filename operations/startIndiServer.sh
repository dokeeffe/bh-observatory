#!/bin/bash

curl http://192.168.1.225:8080/power/mount/on
curl http://192.168.1.225:8080/power/heaters/on
curl http://192.168.1.225:8080/power/ccd/on
curl http://192.168.1.225:8080/power/focuser/on

printf "\n\nEquipement powered on\n\n"

sleep 5

nohup indiserver -v -l /home/dokeeffe indi_ioptronv3_telescope indi_script_dome indi_sx_ccd indi_atik_ccd indi_atik_wheel indi_ipfocuser indi_weather_safety_proxy indi_sqm_weather indi_watchdog &

printf "\n\n Started Indi server \n\n"
