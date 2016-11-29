#!/bin/bash
BASEDIR=$(dirname "$0")
echo "$BASEDIR"
/usr/bin/python "$BASEDIR/schedulerShutdown.py"
