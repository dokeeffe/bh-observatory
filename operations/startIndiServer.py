#!/usr/bin/env python
import subprocess
import json, requests

url = 'http://localhost:8080/power'
power_resp = requests.get(url=url).json()
print('ccd {} mount {}'.format(power_resp['ccd'], power_resp['mount']))
if(power_resp['ccd'] == 'ON' and power_resp['mount'] == 'ON'):
    print('starting')
    subprocess.call(['indiserver','-v','-l','/home/dokeeffe','indi_auxremote','indi_aldiroof','indi_sx_ccd','indi_atik_ccd','indi_ipfocuser','indi_atik_wheel','indi_cloud_rain_monitor'])
else:
    print('no power')
