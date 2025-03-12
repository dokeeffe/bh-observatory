#!/usr/bin/env python3
import requests, shutil
import subprocess
import re
import os
from datetime import datetime, timedelta

def create_night_directory(base_path=".", date_format="%Y-%m-%d"):
    """
    Create a directory for storing night images that span across midnight.

    Args:
        base_path (str): The base directory path where the new directory will be created
        date_format (str): Format for the date in the directory name
 
    Returns:
        str: Path to the created directory
    """
    # Get current date and time
    now = datetime.now()

    # Determine if we're currently in the evening or early morning
    if now.hour >= 18:  # Evening (6PM-11:59PM)
        start_date = now.date()
        end_date = (now + timedelta(days=1)).date()
    else:  # Early morning (12AM-6AM)
        start_date = (now - timedelta(days=1)).date()
        end_date = now.date()

    # Format the directory name
    dir_name = f"Night_{start_date.strftime(date_format)}_to_{end_date.strftime(date_format)}"

    # Create the full path
    dir_path = os.path.join(base_path, dir_name)

    # Create the directory if it doesn't exist
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Created directory: {dir_path}")
    else:
        print(f"Directory already exists: {dir_path}")

    return dir_path

def get_cam_ip():
    output = subprocess.check_output("foscam-search-tool | grep Observatory", shell=True, text=True)
    ip_address = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", output)
    if ip_address:
        ip_address = ip_address.group(0)
    else:
        ip_address = None
    return ip_address

def take_snapshot(cam_ip_address, target_dir):
    img_url= f'http://{cam_ip_address}:88/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr=dokeeffe&pwd=Doohan21*'
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    unique_filename = f"snapshot_{formatted_datetime}.jpg"

    response = requests.get(img_url, stream=True)
    with open(f'{target_dir}/{unique_filename}', 'wb') as fout:
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, fout)



roof = requests.get('http://roof.local:8080/roof')
if roof.status_code == 200:
    json_data = roof.json()
    if json_data['state'] == 'OPEN':
        target_dir = create_night_directory('/home/dokeeffe/Pictures/sec-cam')
        take_snapshot(get_cam_ip(), target_dir)
