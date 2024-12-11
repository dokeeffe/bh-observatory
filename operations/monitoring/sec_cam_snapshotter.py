#!/usr/bin/env python3
import requests, shutil, datetime
import subprocess
import re

def get_cam_ip():
    output = subprocess.check_output("foscam-search-tool | grep Observatory", shell=True, text=True)
    ip_address = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", output)
    if ip_address:
        ip_address = ip_address.group(0)
    else:
        ip_address = None
    return ip_address

def take_snapshot(cam_ip_address):
    img_url= f'http://{cam_ip_address}:88/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr=dokeeffe&pwd=Doohan21*'
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    unique_filename = f"snapshot_{formatted_datetime}.jpg"

    response = requests.get(img_url, stream=True)
    with open(f'/home/dokeeffe/Pictures/sec-cam/{unique_filename}', 'wb') as fout:
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, fout)



roof = requests.get('http://roof.local:8080/roof')
if roof.status_code == 200:
    json_data = roof.json()
    if json_data['state'] == 'OPEN':
        take_snapshot(get_cam_ip())
