#!/usr/bin/env python

import configparser
import os, sys

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
                                      config_to_str('TEXTLOCAL_SMS', 'phonenumber'), test_flag=0)
    message_sender.send_message('Observatory '+sys.argv[1])
