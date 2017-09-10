#!/usr/bin/env bash

# This script will send slack messages containing interesting events from the INDI/EKOS logs.
# See the grep below which is filtering these events.
# You need a file called .slack.conf containing your webhook url. An example is provided below
# WEBHOOK_URL="https://hooks.slack.com/services/T54HDJ6JD/J6JVFS54GO/GR678r5f764e3WD65rg678"
#
source ~/.slack.conf
LATEST_LOG_FILE=$(find ~/.local/share/kstars/logs/ -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -f2- -d" ")
echo 'monitoring' $LATEST_LOG_FILE
tail -f $LATEST_LOG_FILE | grep 'Aborting\|ailed\|candidate job\|Scheduler: Find next job\|Scheduler:  \"Slewing to\|Target is within acceptable range\|Autofocus in progress\|Autofocus complete after\|Shutdown complete\|Roof is open\|Mount is parked\|unparked\|Parking mount\|Starting guiding procedure\|Scheduler: Get next action\|DEBG - Capture:  \"Received image \|Cant contact weather device\|bad weather\|severe weather' | while read line; do
    POST_MSG=$(eval echo $line | cut -d " " -f5-)
    curl -X POST -H 'Content-type: application/json' --data '{"text":"'"$POST_MSG"'"}' $WEBHOOK_URL
done