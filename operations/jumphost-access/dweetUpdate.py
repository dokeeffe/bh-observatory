#!/usr/bin/python
import psycopg2
import urllib2
import json
import requests
import subprocess
import pickle
import time

mainControlSystemHost = "192.168.1.226"
focuserHost = "192.168.1.203"
weatherHost = "192.168.1.227"
mainControlSystemState = 'offline'
weatherSystemState = 'offline'
focuserSystemState = 'offline'
roofState = 'closed'


def pingHost(host):
    ping = subprocess.Popen(
        ["ping", "-c", "1", host],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    out, error = ping.communicate()
    if (not 'Unreachable' in out):
        return True
    else:
        return False


def roofParked():
    getParked = subprocess.Popen(
        ["indi_eval", "-h", "192.168.1.226", "-f",
            "\"Aldi Roof.DOME_PARK.PARK\"==1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    out, error = getParked.communicate()
    # indi_eval outputs to stderr for some reason...
    if ('0' in error):
        return False
    else:
        return True


if (pingHost(mainControlSystemHost) == True):
    mainControlSystemState = 'online'
if (pingHost(weatherHost) == True):
    weatherSystemState = 'online'
if (pingHost(focuserHost) == True):
    focuserSystemState = 'online'
if (roofParked() == False):
    roofState = 'open'

power_req = urllib2.Request("http://localhost:8080/power")
opener = urllib2.build_opener()
resp = opener.open(power_req)
power_json = resp.read()

skyTemp = '0'
rain = 'unknown'
outsideTemp = '0'
observingConditionsOk = False
if (weatherSystemState == 'online'):
    req = urllib2.Request("http://192.168.1.227:8080/weather/current")
    opener = urllib2.build_opener()
    f = opener.open(req)
    json = json.loads(f.read())
    skyTemp = json['skyTemp']
    rain = json['rain']
    outsideTemp = json['outsideTemp']

    # Determine observing conditions, ok or not-ok. If ok for 20min then set
    # observingConditionsOk to True
    if (rain == False and skyTemp < -5):
        print('looks ok, no rain and clear')
        currentTime = time.time()
        try:
            lastRecordedOkTime = pickle.load(open("/tmp/weatherstate.p", "rb"))
        except:
            lastRecordedOkTime = 9999999999
        print('lastrecorded')
        print(lastRecordedOkTime)
        print(currentTime)
        if (currentTime - lastRecordedOkTime > 20 * 60):
            print('looking good for the last 20min')
            observingConditionsOk = True
        else:
            if (lastRecordedOkTime == 9999999999):
                print('storing ok time')
                pickle.dump(currentTime,  open("/tmp/weatherstate.p", "wb"))
    else:
        print('not ok, clearing last recoded ok time')
        pickle.dump(9999999999,  open("/tmp/weatherstate.p", "wb"))


# post to dweet
payload = {'powerSwitches': power_json, 'mainControlSystem': mainControlSystemState, 'weatherSystem': weatherSystemState, 'focuserSystem': focuserSystemState,
           'roof': roofState, 'sky': skyTemp, 'ambientTemp': outsideTemp, 'rain': rain, 'observingConditionsOk': observingConditionsOk}
r = requests.post(
    "http://dweet.io/dweet/for/ballyhouraobservatory?key=1DvBrct97lLdGZel2duY6T", data=payload)
print(r.text)
