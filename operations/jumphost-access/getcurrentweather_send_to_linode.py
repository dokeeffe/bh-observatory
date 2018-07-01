#! /usr/bin/env python
import time,os
from subprocess import call
import urllib

urllib.urlretrieve('http://192.168.1.227:8080/weather/current', '/tmp/current.json')
call(['scp', '/tmp/current.json', 'dokeeffe@52-8.xyz:/var/www/html/images/.'])
urllib.urlretrieve('http://192.168.1.227:8080/weather/history', '/tmp/history.json')
call(['scp', '/tmp/history.json', 'dokeeffe@52-8.xyz:/var/www/html/images/.'])
