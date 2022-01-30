#!/bin/bash

curl http://192.168.1.225:8080/power/mount/on
curl http://192.168.1.225:8080/power/heaters/on
curl http://192.168.1.225:8080/power/ccd/on
curl http://192.168.1.225:8080/power/focuser/on

printf "\n\nEquipement powered on\n\n"

sleep 5

#DSLR only
#nohup indiserver -l /home/dokeeffe indi_ioptronv3_telescope indi_sx_ccd indi_atik_wheel indi_moonlite_focus wheel indi_cloud_rain_monitor indi_sqm_weather indi_watchdog indi_canon_ccd &

#ATIK only
nohup indiserver -v -l /home/dokeeffe indi_ioptronv3_telescope indi_script_dome indi_sx_ccd indi_atik_ccd indi_ipfocuser indi_atik_wheel indi_cloud_rain_monitor indi_sqm_weather indi_watchdog &

#Both
#nohup indiserver -v -l /home/dokeeffe indi_ioptronv3_telescope indi_script_dome indi_sx_ccd indi_atik_ccd indi_ipfocuser indi_atik_wheel indi_cloud_rain_monitor indi_sqm_weather indi_watchdog indi_canon_ccd &


printf "\n\n Started Indi server \n\n"
