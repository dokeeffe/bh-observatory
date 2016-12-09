import urllib
from urllib.request import urlopen
from urllib.parse import urlencode


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
        values = {'test': self.test_flag,
                  'uname': self.user,
                  'hash': self.apikey,
                  'message': message,
                  'from': sender,
                  'selectednums': numbers}

        url = 'http://www.txtlocal.com/sendsmspost.php'
        postdata = urlencode(values)
        try:
            response = self.send_request(url, postdata)
            response_url = response.geturl()
            print(dir(response))
            if response_url == url:
                print('SMS sent! ' + message)
        except urllib.error.URLError as e:
            print('SMS Send failed!')
            print(e.reason)

    def send_request(self, url, postdata):
        return urlopen(url, postdata.encode('UTF-8'))
