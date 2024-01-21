import configparser
import urllib.request
import urllib.parse

import os

import sys

class SmsMessageSender(object):
    '''
    Message sender that uses txtlocal.com gateway to send SMS
    '''
    def __init__(self, user, apikey, phonenumber, test_flag=1):
        '''

        :param user: user
        :param apikey: key
        :param phonenumber: number to send sms
        :param test_flag: 1 for test 0 to send sms
        '''
        self.user = user
        self.apikey = apikey
        self.phonenumber = phonenumber
        self.test_flag = test_flag


    def send_message(self, message):
        '''
        Simple SMS sender based on textlocal.com
        :param message:
        :return:
        '''
        sender = 'OBSERVATORY'
        numbers = (self.phonenumber)
        values = {'apikey' : self.apikey,
                  'message' : message,
                  'sender' : sender,
                  'numbers' : numbers }

        print(values)

        url = 'https://api.txtlocal.com/send/?'
        postdata = urllib.parse.urlencode(values)
        postdata = postdata.encode('utf-8')
        req = urllib.request.Request(url)
        try:
            f = urllib.request.urlopen(req, postdata)
            fr = f.read()
            print(fr)
        except Exception as ex:
            print('SMS Send failed!')
            print(ex)

def config_to_str(group, key):
    return str(config.get(group,key))

if __name__ == '__main__':
    config = configparser.ConfigParser()
    basedir = os.path.dirname(os.path.realpath(__file__))
    config.read(basedir + '/ops.cfg')
    message_sender = SmsMessageSender(config_to_str('TEXTLOCAL_SMS', 'user'), config_to_str('TEXTLOCAL_SMS', 'apikey'),
                                      config_to_str('TEXTLOCAL_SMS', 'phonenumber'), test_flag=0)
    message_sender.send_message('Observatory '+sys.argv[1])
