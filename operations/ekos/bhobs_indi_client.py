#!/usr/bin/env python

import PyIndi
import time

class BhObservatoryIndiClient(PyIndi.BaseClient):
    def __init__(self, host, port):
        super(BhObservatoryIndiClient, self).__init__()
        self.setServer(host,port)

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


class BhObservatoryIndiAdapter():
    '''
    Simple Indi client used to communicate with telescope, roof and ccd drivers for a startup and shutdown procedure.
    The adapter pattern is used to make this code easier to unit test.
    '''

    def __init__(self, indi_client, roof_name, telescope_name, ccd_name):
        self.indi_client = indi_client
        self.roof_name = roof_name
        self.telescope_name = telescope_name
        self.ccd_name = ccd_name
        self.retry_limit=30
        self.indi_client.connectServer()

    def connectServer(self):
        return self.indi_client.connectServer()

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

    def open_roof(self):
        '''
        Tries to open the roof, returns true if the roof is opened
        :param roof_name:
        :return:
        '''
        print('opening roof ')
        device_roof = self.safe_retry(self.indi_client.getDevice, self.roof_name)
        roof_connect = self.safe_retry(device_roof.getSwitch, 'CONNECTION')
        if not (device_roof.isConnected()):
            roof_connect[0].s = PyIndi.ISS_ON  # the 'CONNECT' switch
            roof_connect[1].s = PyIndi.ISS_OFF  # the 'DISCONNECT' switch
            self.indi_client.sendNewSwitch(roof_connect)  # send this new value to the device
        roof_motion = self.safe_retry(device_roof.getSwitch, 'DOME_MOTION')
        roof_motion[0].s = PyIndi.ISS_ON
        roof_motion[1].s = PyIndi.ISS_OFF
        self.indi_client.sendNewSwitch(roof_motion)  # send this new value to the device
        self.wait_for_roof('OPEN')
        print('roof open ')

    def wait_for_roof(self, required_state):
        '''
        Wait for the roof to reach a required state, raise a RuntimeError if it fails to reach the state within 30sec
        :param roof_name:
        :param required_state:
        :return:
        '''
        print('checking ' + self.roof_name)
        device_roof = self.safe_retry(self.indi_client.getDevice, self.roof_name)
        roof_connect = self.safe_retry(device_roof.getSwitch, 'CONNECTION')
        if not (device_roof.isConnected()):
            roof_connect[0].s = PyIndi.ISS_ON  # the 'CONNECT' switch
            roof_connect[1].s = PyIndi.ISS_OFF  # the 'DISCONNECT' switch
            self.indi_client.sendNewSwitch(roof_connect)  # send this new value to the device
        retry = 0
        while retry < self.retry_limit:
            roof_state = device_roof.getText('STATE')
            actual_state = str(roof_state[0].text) if roof_state else 'UNKNOWN'
            if actual_state == required_state:
                return
            print('actual roof state:' + actual_state)
            time.sleep(1)
            retry +=1
        raise RuntimeError('Roof did not reach ' + required_state + ' within 30sec')

    def unpark_scope(self):
        '''
        Unpark the telescope
        :param telescope_name:
        :return:
        '''
        print('start unpark')
        device_telescope = self.safe_retry(self.indi_client.getDevice, self.telescope_name)
        telescope_connect = self.safe_retry(device_telescope.getSwitch, 'CONNECTION')
        if not (device_telescope.isConnected()):
            telescope_connect[0].s = PyIndi.ISS_ON  # the 'CONNECT' switch
            telescope_connect[1].s = PyIndi.ISS_OFF  # the 'DISCONNECT' switch
            self.indi_client.sendNewSwitch(telescope_connect)  # send this new value to the device
        telescope_park = self.safe_retry(device_telescope.getSwitch, 'TELESCOPE_PARK')
        parked = telescope_park[0].s == PyIndi.ISS_ON
        if parked:
            telescope_park[0].s = PyIndi.ISS_OFF
            telescope_park[1].s = PyIndi.ISS_ON
            print('unparking scope')
            self.indi_client.sendNewSwitch(telescope_park)  # send this new value to the device
        else:
            print('scope already unparked')

    def send_guide_pulse_to_mount(self):
        '''
        The single guide pulse is needed as the CPC1100 has a weird quirk that the first guide pulse sent through the
        driver after startup causes the mount to move a couple of arcmin.
        This causes problems with the very first target being imaged.
        Sending a single guide pulse before any work starts is a workaround for this Celestron weirdness

        :param telescope_name:
        :return:
        '''
        device_telescope = self.safe_retry(self.indi_client.getDevice)
        telescope_connect = self.safe_retry(device_telescope.getSwitch, 'CONNECTION')
        if not (device_telescope.isConnected()):
            telescope_connect[0].s = PyIndi.ISS_ON  # the 'CONNECT' switch
            telescope_connect[1].s = PyIndi.ISS_OFF  # the 'DISCONNECT' switch
            self.indi_client.sendNewSwitch(telescope_connect)  # send this new value to the device
        pulse_guide = self.safe_retry(device_telescope.getNumber, 'TELESCOPE_TIMED_GUIDE_NS')
        pulse_guide[0].value = 20
        print('sending pulse guide ')
        self.sendNewNumber(pulse_guide)


    def telescope_parked(self):
        '''
        Return true if the telescope is parked
        :param telescope_name:
        :return:
        '''
        device_telescope = self.safe_retry(self.indi_client.getDevice, self.telescope_name)
        telescope_connect = self.safe_retry(device_telescope.getSwitch, 'CONNECTION')
        if not (device_telescope.isConnected()):
            telescope_connect[0].s = PyIndi.ISS_ON  # the 'CONNECT' switch
            telescope_connect[1].s = PyIndi.ISS_OFF  # the 'DISCONNECT' switch
            self.indi_client.sendNewSwitch(telescope_connect)  # send this new value to the device

        telescope_park = self.safe_retry(device_telescope.getSwitch, 'TELESCOPE_PARK')
        return telescope_park[0].s == PyIndi.ISS_ON

    def close_roof(self):
        '''
        Press the 'close' button on the roof passed. Works with indi rolloff simulator and custom roll off roofs only
        :param roof_name:
        :return:
        '''
        device_roof = self.safe_retry(self.indi_client.getDevice, self.roof_name)
        roof_connect = self.safe_retry(device_roof.getSwitch, 'CONNECTION')
        if not (device_roof.isConnected()):
            roof_connect[0].s = PyIndi.ISS_ON  # the 'CONNECT' switch
            roof_connect[1].s = PyIndi.ISS_OFF  # the 'DISCONNECT' switch
            self.indi_client.sendNewSwitch(roof_connect)  # send this new value to the device
        roof_motion = self.safe_retry(device_roof.getSwitch, 'DOME_MOTION')
        roof_motion[0].s = PyIndi.ISS_OFF
        roof_motion[1].s = PyIndi.ISS_ON
        self.indi_client.sendNewSwitch(roof_motion)  # send this new value to the device
        self.wait_for_roof('CLOSED')

    def set_ccd_temp(self, temp):
        '''
        Set the cooler temp on the ccd passed
        :param ccd_name:
        :param temp:
        :return:
        '''
        print('setting ccd temp for ' + self.ccd_name)
        device_ccd = self.safe_retry(self.indi_client.getDevice, self.ccd_name)
        ccd_connect = self.safe_retry(device_ccd.getSwitch, 'CONNECTION')
        if not (device_ccd.isConnected()):
            ccd_connect[0].s = PyIndi.ISS_ON  # the 'CONNECT' switch
            ccd_connect[1].s = PyIndi.ISS_OFF  # the 'DISCONNECT' switch
            self.indi_client.sendNewSwitch(ccd_connect)  # send this new value to the device
        ccd_temp = device_ccd.getNumber('CCD_TEMPERATURE')
        ccd_temp[0].value=temp
        self.indi_client.sendNewNumber(ccd_temp)
        time.sleep(5) # need to wait for the cooler to kick in

    def get_ccd_temp(self):
        '''
        Get the current ccd cooler temp
        :param ccd_name:
        :return:
        '''
        print('getting ccd temp for ' + self.ccd_name)
        device_ccd = self.safe_retry(self.indi_client.getDevice, self.ccd_name)
        ccd_connect = self.safe_retry(device_ccd.getSwitch, 'CONNECTION')
        if not (device_ccd.isConnected()):
            ccd_connect[0].s = PyIndi.ISS_ON  # the 'CONNECT' switch
            ccd_connect[1].s = PyIndi.ISS_OFF  # the 'DISCONNECT' switch
            self.indi_client.sendNewSwitch(ccd_connect)  # send this new value to the device
        ccd_temp = device_ccd.getNumber('CCD_TEMPERATURE')
        print('temp='+str(ccd_temp[0].value))
        return ccd_temp[0].value


if __name__ == '__main__':
    ic = BhObservatoryIndiClient("localhost", 7624)
    indi = BhObservatoryIndiAdapter(ic,'RollOff Simulator','Telescope Simulator','CCD Simulator')
    indi.wait_for_roof('OPEN')
