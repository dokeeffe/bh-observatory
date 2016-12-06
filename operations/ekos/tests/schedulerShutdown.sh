#!/bin/bash
BASEDIR=$(dirname "$0")
echo "$BASEDIR"
/usr/bin/python3 "$BASEDIR/scheduler_workflow_script.py" shutdown
