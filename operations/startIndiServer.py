#!/usr/bin/env python

import requests
import subprocess
import os

indi_start_command = ['nohup','indiserver','-v','-l','/home/dokeeffe','indi_celestron_gps','indi_aldiroof','indi_asi_ccd','indi_atik_ccd','indi_ipfocuser','indi_atik_wheel','indi_cloud_rain_monitor']

r = requests.get('http://192.168.1.225:8080/power')
state = r.json()

if state['ccd'] == 'ON':
    print 'CCD is on, starting indi services'
    subprocess.Popen(indi_start_command,
                     stdout=open('indi_server.log', 'a'),
                     stderr=open('indi_server.log', 'a'),
                     preexec_fn=os.setpgrp
                     )
    print 'started indi services'
else:
    print 'CCD power is off. Not starting indi services'
