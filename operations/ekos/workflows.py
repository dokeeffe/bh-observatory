import time
import subprocess

class BaseWorkflow(object):
    '''
    These workflows are intended to be triggered by ekos scheduler on startup and shutdown
    '''
    def __init__(self, indi_client, roof_inspector, message_sender, power_controller, config):
        self.indi_client = indi_client
        self.roof_inspector = roof_inspector
        self.message_sender = message_sender
        self.power_controller = power_controller
        self.roof_name = config.get('INDI_DEVICES', 'roof')
        self.telescope_name = config.get('INDI_DEVICES', 'telescope')
        self.ccd_name = config.get('INDI_DEVICES', 'ccd')
        self.powerswitcher_api = config.get('DEVICES', 'powerswitcher_api')


class StartupWorkflow(BaseWorkflow):
    '''
    Startup workflow, performs startup procedures and safety checks.
    '''
    def start(self):
        '''
        Perform the following
            Open the roof
            Unpark the mount
            Send a guide pulse to the mount (see docs in BhObservatoryIndiClient)
            Set ccd temp to -20
            Perform a check of the roof switches
        :return:
        '''
        try:
            if not self.indi_client.connectServer():
                print 'indi not running\n'
                raise Exception('Exception: No indiserver running')
            self.indi_client.open_roof(self.roof_name)
            self.message_sender.send_message('Roof Open http://52-8.xyz/images/snapshot.jpg')
            self.indi_client.unpark_scope(self.telescope_name)
            self.indi_client.send_guide_pulse_to_mount(self.telescope_name)
            self.indi_client.set_ccd_temp(self.ccd_name, -20)
            if self.roof_inspector.query() != 'OPEN':
                raise Exception('Roof did not open')
        except Exception as e:
            print('Sending exception SMS. Cause: \n' + e.message)
            self.message_sender.send_message('ERROR: in startup procedure ' + e.message)
            raise e


class ShutdownWorkflow(BaseWorkflow):

    def start(self):
        '''
        Performs the following
            close the roof
            warm ccd (may be done already but check to be safe)
            poweroff all equipment except mount
            TODO: take necessary dark frames and calibrate data
            poweroff pc
        :return:
        '''
        self._close_roof()
        self._warm_ccd()
        self.power_controller.poweroff_equipment()
        self.power_controller.poweroff_pc()

    def _close_roof(self):
        '''
        Close the roof if the scope is parked, send alert message.
        :return:
        '''
        try:
            if self.indi_client.telescope_parked(self.telescope_name):
                print('Telescope reports parked but this could also mean its parking so wait before closing roof ')
                time.sleep(10)
                self.indi_client.close_roof(self.roof_name)
                if self.roof_inspector.query() == 'CLOSED':
                    self.message_sender.send_message('Roof Closed http://52-8.xyz/images/snapshot.jpg')
                else:
                    self.message_sender.send_sms('Exception: Roof Did not Close http://52-8.xyz/images/snapshot.jpg')
            else:
                print('Sending exception SMS. Scope not parked ')
                self.message_sender.send_sms('Exception: cannot close roof as the telescope is not parked')
        except Exception as e:
            print('Sending exception SMS. Cause: \n' + e.message)
            self.message_sender.send_sms('ERROR: closing roof ' + e.message)
            raise e

    def _warm_ccd(self):
        '''
        Warm the CCD
        :return:
        '''
        self.indiclient.set_ccd_temp(self.ccd_name, 0.0)
        retry = 0
        while self.indiclient.get_ccd_temp(self.ccd_name) < -5 and retry < 300:
            time.sleep(1)
            retry += 1

class PowerController(object):

    def __init__(self ,powerswitcher_api):
        self.powerswitcher_api = powerswitcher_api

    def poweroff_equipment(self):
        '''
        Poweroff all devices EXCEPT the mount.
        The mount is connected to the this PC via USB which supplies 5v and must be powered down after the main PC shutsdown. Otherwise wierd shit happens.
        poweroff the pc with dbus-send --system --print-reply --dest="org.freedesktop.login1" /org/freedesktop/login1 org.freedesktop.login1.Manager.PowerOff boolean:true
        :return:
        '''
        subprocess.call(['curl', self.powerswitcher_api+'/ccd/off'])
        subprocess.call(['curl', self.powerswitcher_api+'/filterwheel/off'])
        subprocess.call(['curl', self.powerswitcher_api+'/heaters/off'])
        subprocess.call(['curl', self.powerswitcher_api+'/focuser/off'])
        subprocess.call(['curl', self.powerswitcher_api+'/aux/off'])

    def poweroff_pc(self):
        '''
        Poweroff the PC using dbus
        :return:
        '''
        subprocess.call(['dbus-send --system --print-reply --dest="org.freedesktop.login1" /org/freedesktop/login1 org.freedesktop.login1.Manager.PowerOff boolean:true'], shell=True)

