!#/bin/bash

#indiserver -v -l /home/dokeeffe indi_celestron_gps indi_asi_ccd indi_atik_ccd indi_atik_wheel indi_ipfocuser
indiserver -v -l /home/dokeeffe indi_celestron_gps indi_aldiroof indi_asi_ccd indi_atik_ccd indi_ipfocuser qik_flat indi_atik_wheel indi_cloud_rain_monitor
#indiserver -vv -l /home/dokeeffe indi_simulator_telescope indi_aldiroof indi_asi_ccd indi_simulator_ccd indi_ipfocuser qik_flat indi_atik_wheel indi_cloud_rain_monitor
