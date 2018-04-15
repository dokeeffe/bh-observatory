#!/bin/bash
BASEDIR=$(dirname "$0")
echo "$BASEDIR"
../../venv/bin/python3 "$BASEDIR/message_senders.py" startup
