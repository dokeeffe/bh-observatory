#! /usr/bin/env python

from platform import system as system_name
from os import system as system_call       
import time
import datetime

def ping(host):
    parameters = "-n 1" if system_name().lower()=="windows" else "-c 1"
    return system_call("ping " + parameters + " " + host) == 0

def internet_connected():
    connected = False
    fail_count = 0
    while not connected and fail_count < 4:
        if not ping('8.8.8.8'):
            print('no internet connection')
            fail_count+=1
        else:
            connected = True
            print('{} - net ok'.format(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")))
    return connected

def power_cycle_net():
    print('{} - Power cycling router and 4G connection devices'.format(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")))
    system_call('curl http://localhost:8080/power/mainsplug/off')
    time.sleep(10)
    system_call('curl http://localhost:8080/power/mainsplug/on')
    
 

if __name__ == '__main__':
    if not internet_connected():
        power_cycle_net()
