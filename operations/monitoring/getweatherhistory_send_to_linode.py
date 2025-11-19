#! /usr/bin/env python
import time,os
from subprocess import call
import urllib.request

urllib.request.urlretrieve('http://192.168.1.227:8080/weather/history', '/tmp/weather-history.json')
call(['scp', '/tmp/weather-history.json', 'dokeeffe@52-8.xyz:/var/www/html/images/telemetry/.'])
