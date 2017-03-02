#!/usr/bin/env python

import configparser
import os, sys

from bhobs_indi_client import BhObservatoryIndiClient, BhObservatoryIndiAdapter
from workflows import StartupWorkflow, ShutdownWorkflow, PowerController
from message_senders import SmsMessageSender

'''
This script gets called from a shell script that EKOS scheduler calls.
See schedulerStarup.sh and schedulerShutdown.sh for details
'''

def config_to_str(group, key):
    return str(config.get(group,key))

if __name__ == '__main__':
    config = configparser.ConfigParser()
    basedir = os.path.dirname(os.path.realpath(__file__))
    config.read(basedir + '/ops.cfg')
    message_sender = SmsMessageSender(config_to_str('TEXTLOCAL_SMS', 'user'), config_to_str('TEXTLOCAL_SMS', 'apikey'),
                                      config_to_str('TEXTLOCAL_SMS', 'phonenumber'), test_flag=1)
    message_sender.send_message('Starting observatory '+sys.argv[1]+' procedure')
    try:
        indiclient = BhObservatoryIndiClient("localhost", 7624)
        indi_wrapper = BhObservatoryIndiAdapter(indiclient, config_to_str('INDI_DEVICES', 'roof'),
                                                config_to_str('INDI_DEVICES', 'telescope'), config_to_str('INDI_DEVICES', 'ccd'))
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
