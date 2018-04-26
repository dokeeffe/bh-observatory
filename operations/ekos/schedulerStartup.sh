#!/bin/bash
BASEDIR=$(dirname "$0")
echo "$BASEDIR"
/usr/bin/python "$BASEDIR/message_senders.py" startup
/usr/bin/python "$BASEDIR/tplink_hs1xx/smartplug.py" 192.168.2.229 OFF

# Check park status of roof and scope, check xml files

# Check weather

# Power off dehunmidifer

# Switch off IR lamps

