#!/usr/bin/env python

import ConfigParser
import PyIndi
import time, logging
import sms


class IndiClient(PyIndi.BaseClient):
    def __init__(self):
        super(IndiClient, self).__init__()

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
        result = func(arg)
        retry = 0
        while not (result) and retry < 10:
            time.sleep(0.5)
            result = func(arg)
            retry += 1
        return result

    def telescope_parked(self, telescope_name):
        device_telescope = self.safe_retry(self.getDevice, telescope_name)
        telescope_connect = self.safe_retry(device_telescope.getSwitch, "CONNECTION")
        if not (device_telescope.isConnected()):
            telescope_connect[0].s = PyIndi.ISS_ON  # the "CONNECT" switch
            telescope_connect[1].s = PyIndi.ISS_OFF  # the "DISCONNECT" switch
            indiclient.sendNewSwitch(telescope_connect)  # send this new value to the device

        telescope_park = self.safe_retry(device_telescope.getSwitch, "TELESCOPE_PARK")
        return telescope_park[0].s == PyIndi.ISS_ON

    def close_roof(self, roof_name):
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
        print 'closing'


config = ConfigParser.ConfigParser()
config.read('ops.cfg')
print config.get('TEXTLOCAL', 'user')
try:
    indiclient = IndiClient()
    indiclient.setServer("localhost", 7624)
    if (not (indiclient.connectServer())):
        raise Exception('Exception: No indiserver running on')
    if indiclient.telescope_parked('Telescope Simulator'):
        logging.info('Telescope reports parked but this could also mean parking so waiting 15sec before closing roof')
        indiclient.close_roof('RollOff Simulator')
        sms.send_sms(config.get('TEXTLOCAL', 'user'), config.get('TEXTLOCAL', 'apikey'),
                     config.get('TEXTLOCAL', 'phonenumber'), 'Roof Closed')
    else:
        sms.send_sms(config.get('TEXTLOCAL', 'user'), config.get('TEXTLOCAL', 'apikey'),
                     config.get('TEXTLOCAL', 'phonenumber'), 'Exception: cannot close roof as the telescope is not parked')
except Exception as e:
    sms.send_sms(config.get('TEXTLOCAL', 'user'), config.get('TEXTLOCAL', 'apikey'),
                 config.get('TEXTLOCAL', 'phonenumber'), 'ERROR: closing roof ' + e.message)
    raise e
