#! /usr/bin/env python
import time
import os
from subprocess import call
from datetime import datetime
import urllib.request
import json

# Paths
CURRENT_FILE = '/tmp/roof.json'
REMOTE_FILE = '/tmp/roof_new.json'

# Get the new state from the roof controller
urllib.request.urlretrieve('http://localhost:8080/roof', REMOTE_FILE)

# Load the new state
with open(REMOTE_FILE, 'r') as f:
    new_data = json.load(f)

# Check if we have a previous state
if os.path.exists(CURRENT_FILE):
    with open(CURRENT_FILE, 'r') as f:
        old_data = json.load(f)

    # If state changed, update the timestamp
    if old_data.get('state') != new_data.get('state'):
        new_data['last_changed'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    else:
        # State unchanged, preserve the old timestamp
        new_data['last_changed'] = old_data.get('last_changed', datetime.now().strftime('%Y-%m-%d %H:%M'))
else:
    # First run, set initial timestamp
    new_data['last_changed'] = datetime.now().strftime('%Y-%m-%d %H:%M')

# Save the updated state locally
with open(CURRENT_FILE, 'w') as f:
    json.dump(new_data, f)

# Upload to website
call(['scp', CURRENT_FILE, 'dokeeffe@52-8.xyz:/var/www/html/images/telemetry/.'])

