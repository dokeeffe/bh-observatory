#!/usr/bin/env python3
import requests, shutil, datetime
import subprocess
from subprocess import call
import re

def get_cam_ip(name):
    output = subprocess.check_output(f'/usr/local/bin/foscam-search-tool | grep {name}', shell=True, text=True)
    ip_address = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", output)
    if ip_address:
        ip_address = ip_address.group(0)
    else:
        ip_address = None
    print(f'found camera {ip_address}')
    return ip_address

def take_snapshot(cam_ip_address, name, ath):
    img_url= f'http://{cam_ip_address}:88/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr=dokeeffe&pwd={ath}'
    print(f'{img_url}')
    response = requests.get(img_url, stream=True)
    with open(f'/tmp/snapshot-{name}.jpg', 'wb') as fout:
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, fout)



take_snapshot(get_cam_ip('Observatory'), 'obs1', 'Doohan21*')
call(['scp', '/tmp/snapshot-obs1.jpg', 'dokeeffe@52-8.xyz:/var/www/html/images/telemetry/.'])
take_snapshot(get_cam_ip('obs2'), 'obs2', 'zxcvbn3')
call(['scp', '/tmp/snapshot-obs2.jpg', 'dokeeffe@52-8.xyz:/var/www/html/images/telemetry/.'])
