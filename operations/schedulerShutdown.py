#!/usr/bin/env python

import ConfigParser
import os

import PyIndi
import time
import sms


class ObservatoryShutdownIndiClient(PyIndi.BaseClient):
    '''
    Simple Indi client used to communicate with telescope, roof and ccd drivers for a shutdown procedure
    '''
    def __init__(self):
        super(ObservatoryShutdownIndiClient, self).__init__()

    def newDevice(self, d):
        pass

    def newProperty(self, p):
        pass

    def removeProperty(self, p):
        pass

    def newBLOB(self, bp):
        pass

    def newSwitch(self, svp):
        pass

    def newNumber(self, nvp):
        pass

    def newText(self, tvp):
        pass

    def newLight(self, lvp):
        pass

    def newMessage(self, d, m):
        pass

    def serverConnected(self):
        pass

    def serverDisconnected(self, code):
        pass

    def safe_retry(self, func, arg):
        '''
        Utility function to safely retry indi functions. Indi functions dont always return the object on the first call as the device may not be ready
        :param func:
        :param arg:
        :return:
        '''
        result = func(arg)
        retry = 0
        while not (result) and retry < 10:
            time.sleep(0.5)
            result = func(arg)
            retry += 1
        return result

    def telescope_parked(self, telescope_name):
        '''
        Return true if the telescope is parked
        :param telescope_name:
        :return:
        '''
        device_telescope = self.safe_retry(self.getDevice, telescope_name)
        telescope_connect = self.safe_retry(device_telescope.getSwitch, "CONNECTION")
        if not (device_telescope.isConnected()):
            telescope_connect[0].s = PyIndi.ISS_ON  # the "CONNECT" switch
            telescope_connect[1].s = PyIndi.ISS_OFF  # the "DISCONNECT" switch
            indiclient.sendNewSwitch(telescope_connect)  # send this new value to the device

        telescope_park = self.safe_retry(device_telescope.getSwitch, "TELESCOPE_PARK")
        return telescope_park[0].s == PyIndi.ISS_ON

    def close_roof(self, roof_name):
        '''
        Press the 'close' button on the roof passed. Works with indi rolloff simulator and custom roll off roofs only
        :param roof_name:
        :return:
        '''
        device_roof = self.safe_retry(self.getDevice, roof_name)
        roof_connect = self.safe_retry(device_roof.getSwitch, "CONNECTION")
        if not (device_roof.isConnected()):
            roof_connect[0].s = PyIndi.ISS_ON  # the "CONNECT" switch
            roof_connect[1].s = PyIndi.ISS_OFF  # the "DISCONNECT" switch
            indiclient.sendNewSwitch(roof_connect)  # send this new value to the device
        roof_motion = self.safe_retry(device_roof.getSwitch, "DOME_MOTION")
        roof_motion[0].s = PyIndi.ISS_OFF  # the "CONNECT" switch
        roof_motion[1].s = PyIndi.ISS_ON  # the "DISCONNECT" switch
        indiclient.sendNewSwitch(roof_motion)  # send this new value to the device
        while roof_motion[1].s == PyIndi.ISS_ON:
            print 'waiting to close \n'
            time.sleep(1)
        print 'closing\n'



def close_roof(roof_name, telescope_name):
    '''
    Safely close the roof. Send an SMS on close or on error
    :param roof_name:
    :param telescope_name:
    :return:
    '''
    global indiclient
    try:
        indiclient = ObservatoryShutdownIndiClient()
        indiclient.setServer("localhost", 7624)
        if (not (indiclient.connectServer())):
            print 'indi not running\n'
            raise Exception('Exception: No indiserver running')
        print 'shutting down3'
        if indiclient.telescope_parked(telescope_name):
            print('Telescope reports parked but this could also mean its parking so waiting 15sec before closing roof\n')
            time.sleep(15)
            indiclient.close_roof(roof_name)
            send_sms('Roof Closed http://52-8.xyz/images/snapshot.jpg')
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


def warm_ccd(ccd_name):
    '''
    Ensure the CCD temp is warm enough to shutdown
    :param ccd_name:
    :return:
    '''
    pass

def poweroff():
    '''
    Poweroff all devices EXCEPT the mount.
    The mount is connected to the main PC via USB which supplies 5v and must be powered down after the main PC shutsdown. Otherwise wierd shit happens.
    :return:
    '''
    pass

print 'Sending shutting down SMS\n'
config = ConfigParser.ConfigParser()
basedir = os.path.dirname(os.path.realpath(__file__))
config.read(basedir+'/ops.cfg')
send_sms('Starting observatory shutdown')
close_roof(config.get('INDI_DEVICES', 'roof'),config.get('INDI_DEVICES', 'telescope'))
warm_ccd(config.get('INDI_DEVICES', 'roof'))



poweroff()

