import configparser
import urllib

import os

import sys
import urllib2

class SmsMessageSender(object):
    '''
    Message sender that uses txtlocal.com gateway to send SMS
    This message sender is only compatable with python 3 because of the way they changed urllib in python3...
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
        values = {'test'    : self.test_flag,
                  'uname'   : self.user,
                  'hash'    : self.apikey,
                  'message' : message,
                  'from'    : sender,
                  'selectednums' : numbers }

        url = 'http://www.txtlocal.com/sendsmspost.php'
        postdata = urllib.urlencode(values)
        req = urllib2.Request(url, postdata)
        try:
            response = urllib2.urlopen(req)
            response_url = response.geturl()
            if response_url==url:
                print('SMS sent! ' + message)
        except Exception:
            print('SMS Send failed!')

def config_to_str(group, key):
    return str(config.get(group,key))

if __name__ == '__main__':
    config = configparser.ConfigParser()
    basedir = os.path.dirname(os.path.realpath(__file__))
    config.read(basedir + '/ops.cfg')
    message_sender = SmsMessageSender(config_to_str('TEXTLOCAL_SMS', 'user'), config_to_str('TEXTLOCAL_SMS', 'apikey'),
                                      config_to_str('TEXTLOCAL_SMS', 'phonenumber'), test_flag=0)
    message_sender.send_message('Observatory '+sys.argv[1])
