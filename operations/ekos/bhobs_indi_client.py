#!/usr/bin/env python

import PyIndi
import time

class BhObservatoryIndiClient(PyIndi.BaseClient):
    '''
    Simple Indi client used to communicate with telescope, roof and ccd drivers for a startup and shutdown procedure.
    '''

    def __init__(self):
        super(BhObservatoryIndiClient, self).__init__()

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

    def open_roof(self, roof_name):
        '''
        Tries to open the roof, returns true if the roof is opened
        :param roof_name:
        :return:
        '''
        print('opening roof ')
        device_roof = self.safe_retry(self.getDevice, roof_name)
        roof_connect = self.safe_retry(device_roof.getSwitch, 'CONNECTION')
        if not (device_roof.isConnected()):
            roof_connect[0].s = PyIndi.ISS_ON  # the 'CONNECT' switch
            roof_connect[1].s = PyIndi.ISS_OFF  # the 'DISCONNECT' switch
            self.sendNewSwitch(roof_connect)  # send this new value to the device
        roof_motion = self.safe_retry(device_roof.getSwitch, 'DOME_MOTION')
        roof_motion[0].s = PyIndi.ISS_ON
        roof_motion[1].s = PyIndi.ISS_OFF
        self.sendNewSwitch(roof_motion)  # send this new value to the device
        # TODO: Check here if the switch state changes before returning true
        time.sleep(15)
        print('roof open ')
        return True


    def unpark_scope(self, telescope_name):
        '''
        Unpark the telescope
        :param telescope_name:
        :return:
        '''
        print('start unpark')
        device_telescope = self.safe_retry(self.getDevice, telescope_name)
        telescope_connect = self.safe_retry(device_telescope.getSwitch, 'CONNECTION')
        if not (device_telescope.isConnected()):
            telescope_connect[0].s = PyIndi.ISS_ON  # the 'CONNECT' switch
            telescope_connect[1].s = PyIndi.ISS_OFF  # the 'DISCONNECT' switch
            self.sendNewSwitch(telescope_connect)  # send this new value to the device
        telescope_park = self.safe_retry(device_telescope.getSwitch, 'TELESCOPE_PARK')
        parked = telescope_park[0].s == PyIndi.ISS_ON
        if parked:
            telescope_park[0].s = PyIndi.ISS_OFF
            telescope_park[1].s = PyIndi.ISS_ON
            print('unparking scope')
            self.sendNewSwitch(telescope_park)  # send this new value to the device
        else:
            print('scope already unparked')

    def send_guide_pulse_to_mount(self, telescope_name):
        '''
        The single guide pulse is needed as the CPC1100 has a weird quirk that the first guide pulse sent through the
        driver after startup causes the mount to move a couple of arcmin.
        This causes problems with the very first target being imaged.
        Sending a single guide pulse before any work starts is a workaround for this Celestron weirdness

        :param telescope_name:
        :return:
        '''
        device_telescope = self.safe_retry(self.getDevice, telescope_name)
        telescope_connect = self.safe_retry(device_telescope.getSwitch, 'CONNECTION')
        if not (device_telescope.isConnected()):
            telescope_connect[0].s = PyIndi.ISS_ON  # the 'CONNECT' switch
            telescope_connect[1].s = PyIndi.ISS_OFF  # the 'DISCONNECT' switch
            self.sendNewSwitch(telescope_connect)  # send this new value to the device
        pulse_guide = self.safe_retry(device_telescope.getNumber, 'TELESCOPE_TIMED_GUIDE_NS')
        pulse_guide[0].value = 20
        print('sending pulse guide ')
        self.sendNewNumber(pulse_guide)


    def telescope_parked(self, telescope_name):
        '''
        Return true if the telescope is parked
        :param telescope_name:
        :return:
        '''
        device_telescope = self.safe_retry(self.getDevice, telescope_name)
        telescope_connect = self.safe_retry(device_telescope.getSwitch, 'CONNECTION')
        if not (device_telescope.isConnected()):
            telescope_connect[0].s = PyIndi.ISS_ON  # the 'CONNECT' switch
            telescope_connect[1].s = PyIndi.ISS_OFF  # the 'DISCONNECT' switch
            self.sendNewSwitch(telescope_connect)  # send this new value to the device

        telescope_park = self.safe_retry(device_telescope.getSwitch, 'TELESCOPE_PARK')
        return telescope_park[0].s == PyIndi.ISS_ON

    def close_roof(self, roof_name):
        '''
        Press the 'close' button on the roof passed. Works with indi rolloff simulator and custom roll off roofs only
        :param roof_name:
        :return:
        '''
        device_roof = self.safe_retry(self.getDevice, roof_name)
        roof_connect = self.safe_retry(device_roof.getSwitch, 'CONNECTION')
        if not (device_roof.isConnected()):
            roof_connect[0].s = PyIndi.ISS_ON  # the 'CONNECT' switch
            roof_connect[1].s = PyIndi.ISS_OFF  # the 'DISCONNECT' switch
            self.sendNewSwitch(roof_connect)  # send this new value to the device
        roof_motion = self.safe_retry(device_roof.getSwitch, 'DOME_MOTION')
        roof_motion[0].s = PyIndi.ISS_OFF
        roof_motion[1].s = PyIndi.ISS_ON
        self.sendNewSwitch(roof_motion)  # send this new value to the device

    def set_ccd_temp(self, ccd_name, temp):
        print('setting ccd temp for ' + ccd_name)
        device_ccd = self.safe_retry(self.getDevice, ccd_name)
        ccd_connect = self.safe_retry(device_ccd.getSwitch, 'CONNECTION')
        if not (device_ccd.isConnected()):
            ccd_connect[0].s = PyIndi.ISS_ON  # the 'CONNECT' switch
            ccd_connect[1].s = PyIndi.ISS_OFF  # the 'DISCONNECT' switch
            self.sendNewSwitch(ccd_connect)  # send this new value to the device
        ccd_temp = device_ccd.getNumber('CCD_TEMPERATURE')
        ccd_temp[0].value=0
        self.sendNewNumber(ccd_temp)
        time.sleep(5) # need to wait for the cooler to kick in

    def get_ccd_temp(self, ccd_name):
        print('getting ccd temp for ' + ccd_name)
        device_ccd = self.safe_retry(self.getDevice, ccd_name)
        ccd_connect = self.safe_retry(device_ccd.getSwitch, 'CONNECTION')
        if not (device_ccd.isConnected()):
            ccd_connect[0].s = PyIndi.ISS_ON  # the 'CONNECT' switch
            ccd_connect[1].s = PyIndi.ISS_OFF  # the 'DISCONNECT' switch
            self.sendNewSwitch(ccd_connect)  # send this new value to the device
        ccd_temp = device_ccd.getNumber('CCD_TEMPERATURE')
        print('temp='+str(ccd_temp[0].value))
        return ccd_temp[0].value

