#!/usr/bin/env python

import ConfigParser
import os, sys

from operations.ekos.bhobs_indi_client import BhObservatoryIndiClient
from fakes import FakeRoofSwitchInspector, FakePowerController
from operations.ekos.message_senders import SmsMessageSender
from operations.ekos.workflows import StartupWorkflow, ShutdownWorkflow

'''
This TEST script is intended to be called from EKOS scheduler running simulators.
'''
if __name__ == '__main__':
    config = ConfigParser.ConfigParser()
    basedir = os.path.dirname(os.path.realpath(__file__))
    config.read(basedir + '/ops.cfg')
    message_sender = SmsMessageSender(config.get('TEXTLOCAL_SMS', 'user'), config.get('TEXTLOCAL_SMS', 'apikey'),
                                      config.get('TEXTLOCAL_SMS', 'phonenumber'), test_flag=1)
    try:
        message_sender.send_message('Starting observatory startup procedure')
        roof_inspector = FakeRoofSwitchInspector('OPEN')
        indiclient = BhObservatoryIndiClient()
        indiclient.setServer("localhost", 7624)
        power_controller = FakePowerController()
        if sys.argv[1] == 'startup':
            workflow = StartupWorkflow(indiclient, roof_inspector, message_sender, power_controller, config)
            workflow.start()
        elif sys.argv[1] == 'shutdown':
            workflow = ShutdownWorkflow(indiclient, roof_inspector, message_sender, power_controller, config)
            workflow.start()
    except Exception as e:
        message_sender.send_message('EXCEPTION: ' + e.__str__())
        raise e
