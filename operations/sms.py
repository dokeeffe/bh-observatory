import urllib      # URL functions
import urllib2     # URL functions

def send_sms(username, hash, number, message):
    '''
    Simple SMS sender based on textlocal.com
    :param username:
    :param hash:
    :param number:
    :param message:
    :return:
    '''
    sender = 'OBSERVATORY'
    test_flag = 1  #1 for test 0 to send sms
    numbers = (number)
    values = {'test'    : test_flag,
              'uname'   : username,
              'hash'    : hash,
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
            print 'SMS sent!'
    except urllib2.URLError, e:
        print 'SMS Send failed!'
        print e.reason
