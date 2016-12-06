import urllib
import urllib2

class SmsMessageSender(object):

    def __init__(self, user, apikey, phonenumber, test_flag=0):
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
        except urllib2.URLError, e:
            print('SMS Send failed!')
            print(e.reason)
