#!/usr/bin/env python

import ConfigParser
import os
import subprocess
import time

import sms
from bhobs_indi_client import BhObservatoryIndiClient
from roofInspector import RoofSwitchInspector


def close_roof(roof_name, telescope_name, roof_inspector, indiclient):
    '''
    Safely close the roof. Send an SMS on close or on error
    :param roof_name:
    :param telescope_name:
    :param roof_inspector
    :param indiclient:
    :return:
    '''
    try:
        if indiclient.telescope_parked(telescope_name):
            print('Telescope reports parked but this could also mean its parking so wait before closing roof\n')
            time.sleep(10)
            indiclient.close_roof(roof_name)
            if roof_inspector.query() == RoofSwitchInspector.CLOSED:
                send_sms('Roof Closed http://52-8.xyz/images/snapshot.jpg')
            else:
                send_sms('Exception: Roof Did not Close http://52-8.xyz/images/snapshot.jpg')
        else:
            print('Sending exception SMS. Scope not parked\n')
            send_sms('Exception: cannot close roof as the telescope is not parked')
    except Exception as e:
        print('Sending exception SMS. Cause: \n' + e.message)
        send_sms('ERROR: closing roof ' + e.message)
        raise e


def send_sms(message):
    '''
    Send an SMS message to operations manager
    :param message:
    :return:
    '''
    sms.send_sms(config.get('TEXTLOCAL_SMS', 'user'), config.get('TEXTLOCAL_SMS', 'apikey'),
                 config.get('TEXTLOCAL_SMS', 'phonenumber'), message)


def warm_ccd(ccd_name, indiclient):
    '''
    Ensure the CCD temp is warm enough to shutdown (-5 should be ok, should take ambient into account)
    :param ccd_name:
    :return:
    '''
    indiclient.set_ccd_temp(ccd_name, 0.0)
    retry = 0
    while indiclient.get_ccd_temp(ccd_name) < -5 and retry < 300:
        time.sleep(1)
        retry += 1

def poweroff():
    '''
    Poweroff all devices EXCEPT the mount, then poweroff the pc.
    The mount is connected to the main PC via USB which supplies 5v and must be powered down after the main PC shutsdown. Otherwise wierd shit happens.
    poweroff the pc with dbus-send --system --print-reply --dest="org.freedesktop.login1" /org/freedesktop/login1 org.freedesktop.login1.Manager.PowerOff boolean:true
    :return:
    '''
    subprocess.call(['curl','http://192.168.2.225:8080/power/ccd/off'])
    subprocess.call(['curl','http://192.168.2.225:8080/power/filterwheel/off'])
    subprocess.call(['curl','http://192.168.2.225:8080/power/heaters/off'])
    subprocess.call(['curl','http://192.168.2.225:8080/power/focuser/off'])
    subprocess.call(['curl','http://192.168.2.225:8080/power/aux/off'])
    subprocess.call(['dbus-send --system --print-reply --dest="org.freedesktop.login1" /org/freedesktop/login1 org.freedesktop.login1.Manager.PowerOff boolean:true'], shell=True)

print 'Sending shutting down SMS\n'
config = ConfigParser.ConfigParser()
basedir = os.path.dirname(os.path.realpath(__file__))
config.read(basedir+'/ops.cfg')
send_sms('Starting observatory shutdown')
indiclient = BhObservatoryIndiClient()
indiclient.setServer("localhost", 7624)
if not indiclient.connectServer():
    send_sms('Aborting shutdown procedure, indi not running')
    raise Exception('Exception: No indiserver running')
roof_inspector = RoofSwitchInspector(config.get('ROOF_CONTROLLER', 'usbaddress'))
close_roof(config.get('INDI_DEVICES', 'roof') ,config.get('INDI_DEVICES', 'telescope'),roof_inspector,indiclient)
warm_ccd(config.get('INDI_DEVICES', 'ccd'), indiclient)
poweroff()
