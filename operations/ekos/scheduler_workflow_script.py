#!/usr/bin/env python

import ConfigParser
import os, sys

from bhobs_indi_client import BhObservatoryIndiClient
from roofInspector import RoofSwitchInspector
from workflows import StartupWorkflow, ShutdownWorkflow, PowerController
from message_senders import SmsMessageSender

'''
This script gets called from a shell script that EKOS scheduler calls.
See schedulerStarup.sh and schedulerShutdown.sh for details
'''
if __name__ == '__main__':
    config = ConfigParser.ConfigParser()
    basedir = os.path.dirname(os.path.realpath(__file__))
    config.read(basedir + '/ops.cfg')
    message_sender = SmsMessageSender(config.get('TEXTLOCAL_SMS', 'user'), config.get('TEXTLOCAL_SMS', 'apikey'),
                                      config.get('TEXTLOCAL_SMS', 'phonenumber'))
    message_sender.send_message('Starting observatory startup procedure')
    try:
        roof_inspector = RoofSwitchInspector(config.get('DEVICES', 'usbaddress'))
        indiclient = BhObservatoryIndiClient()
        indiclient.setServer("localhost", 7624)
        power_controller = PowerController(config.get('DEVICES', 'powerswitcher_api'))
        if sys.argv[1] == 'startup':
            workflow = StartupWorkflow(indiclient, roof_inspector, message_sender, power_controller, config)
            workflow.start()
        elif sys.argv[1] == 'shutdown':
            workflow = ShutdownWorkflow(indiclient, roof_inspector, message_sender, power_controller, config)
            workflow.start()
    except Exception as e:
        message_sender.send_message('EXCEPTION: ' + e.__str__())
        raise e

