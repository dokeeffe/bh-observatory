#! /usr/bin/env python
import time,os
from subprocess import call
import urllib

urllib.urlretrieve('http://192.168.2.227:8080/weather/chart/temperature.png', '/tmp/temperature.png')
urllib.urlretrieve('http://192.168.2.227:8080/weather/chart/cloud.png', '/tmp/cloud.png')

call(['scp', '/tmp/temperature.png', 'dokeeffe@52-8.xyz:/var/www/html/images/.'])
call(['scp', '/tmp/cloud.png', 'dokeeffe@52-8.xyz:/var/www/html/images/.'])
