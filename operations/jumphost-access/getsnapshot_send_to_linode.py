#! /usr/bin/env python
import time,os
from subprocess import call
import json, requests
import urllib2

'''
Script to upload an image from the security camera with a watermark containing time weather and power states
'''
power_resp = requests.get(url='http://localhost:8080/power')
switch_states = json.loads(power_resp.text)
time_string  = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
power = ''
if switch_states['heaters'] == 'ON':
    power += 'heater '
if switch_states['mount'] == 'ON':
    power += 'mount '
if switch_states['ccd'] == 'ON':
    power += 'ccd '
if switch_states['filterwheel'] == 'ON':
    power += 'efw '
if switch_states['focuser'] == 'ON':
    power += 'focuser '
if switch_states['aux'] == 'ON':
    power += 'light-panel '

main_pc = 'offline'
if os.system("ping -c 1 192.168.1.226") == 0:
    main_pc = 'online'

watermark = 'System:' + main_pc + ' ' + power + '\n' + time_string + '                     Ballyhoura Observatory'
req = urllib2.Request('http://192.168.1.222/snapshot.cgi')
req.add_header('Authorization', 'Basic YWRtaW46enhjdmJuMw==')
resp = urllib2.urlopen(req)
with open('/tmp/snapshot.jpg','wb') as output:
  output.write(resp.read())

call(['/usr/bin/convert', '/tmp/snapshot.jpg', '-pointsize', '22', '-fill', 'white', '-annotate', '+5+415', watermark, '/tmp/snapshot.jpg'])
call(['scp', '/tmp/snapshot.jpg', 'dokeeffe@52-8.xyz:/var/www/html/images/telemetry/.'])


req = urllib2.Request('http://192.168.1.221:88/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr=dokeeffe&pwd=zxcvbn3')
resp = urllib2.urlopen(req)
with open('/tmp/cam2-snapshot.jpg','wb') as output:
  output.write(resp.read())
call(['scp', '/tmp/cam2-snapshot.jpg', 'dokeeffe@52-8.xyz:/var/www/html/images/telemetry/.'])

