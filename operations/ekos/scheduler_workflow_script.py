#!/usr/bin/env python

import configparser
import os, sys

from bhobs_indi_client import BhObservatoryIndiClient
from workflows import StartupWorkflow, ShutdownWorkflow, PowerController
from message_senders import SmsMessageSender

'''
This script gets called from a shell script that EKOS scheduler calls.
See schedulerStarup.sh and schedulerShutdown.sh for details
'''
if __name__ == '__main__':
    config = configparser.ConfigParser()
    basedir = os.path.dirname(os.path.realpath(__file__))
    config.read(basedir + '/ops.cfg')
    message_sender = SmsMessageSender(config.get('TEXTLOCAL_SMS', 'user'), config.get('TEXTLOCAL_SMS', 'apikey'),
                                      config.get('TEXTLOCAL_SMS', 'phonenumber'))
    message_sender.send_message('Starting observatory startup procedure')
    try:
        indiclient = BhObservatoryIndiClient("localhost", 7624)
        indi_wrapper = BhObservatoryIndiClient(indiclient, config.get('INDI_DEVICES', 'roof'),
                                             config.get('INDI_DEVICES', 'telescope'), config.get('INDI_DEVICES', 'ccd'))
        power_controller = PowerController(config.get('DEVICES', 'powerswitcher_api'))
        if sys.argv[1] == 'startup':
            workflow = StartupWorkflow(indi_wrapper, message_sender, power_controller, config)
            workflow.start()
        elif sys.argv[1] == 'shutdown':
            workflow = ShutdownWorkflow(indi_wrapper, message_sender, power_controller, config)
            workflow.start()
    except Exception as e:
        message_sender.send_message('EXCEPTION: ' + e.__str__())
        raise e
