#!/bin/bash
BASEDIR=$(dirname "$0")
echo "$BASEDIR"
../../venv/bin/python3 "$BASEDIR/message_senders.py" startup
../../venv/bin/python3 "$BASEDIR/tplink_hs1xx/smartplug.py" 192.168.2.229 OFF

# Check park status of roof and scope, check xml files

# Check weather

# Power off dehunmidifer

# Switch off IR lamps

