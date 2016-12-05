#!/usr/bin/env python

import ConfigParser
import os

import sms
from bhobs_indi_client import BhObservatoryIndiClient


def startup_procedure(roof_name, telescope_name, ccd_name):
    '''
    Open the roof, unpark the mount, send a guide pulse to the mount (see docs in BhObservatoryIndiClient),
    set ccd temp to -20
    :param roof_name:
    :param telescope_name:
    :return:
    '''
    indiclient = BhObservatoryIndiClient()
    try:
        indiclient.setServer("localhost", 7624)
        if not indiclient.connectServer():
            print 'indi not running\n'
            raise Exception('Exception: No indiserver running')
        #indiclient.open_roof(roof_name)
        send_sms('Roof Open http://52-8.xyz/images/snapshot.jpg')
        indiclient.unpark_scope(telescope_name)
        indiclient.send_guide_pulse_to_mount(telescope_name)
        indiclient.set_ccd_temp(ccd_name, -20)
    except Exception as e:
        print('Sending exception SMS. Cause: \n' + e.message)
        send_sms('ERROR: in startup procedure ' + e.message)
        raise e

def send_sms(message):
    '''
    Send an SMS message to operations manager
    :param message:
    :return:
    '''
    sms.send_sms(config.get('TEXTLOCAL_SMS', 'user'), config.get('TEXTLOCAL_SMS', 'apikey'),
                 config.get('TEXTLOCAL_SMS', 'phonenumber'), message)



print('Sending startup SMS')
config = ConfigParser.ConfigParser()
basedir = os.path.dirname(os.path.realpath(__file__))
config.read(basedir + '/ops.cfg')
send_sms('Starting observatory startup procedure')
startup_procedure(config.get('INDI_DEVICES', 'roof'), config.get('INDI_DEVICES', 'telescope'), config.get('INDI_DEVICES', 'ccd'))
