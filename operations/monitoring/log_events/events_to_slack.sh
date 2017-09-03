#!/usr/bin/env bash
source ~/.slack.conf
LATEST_LOG_FILE=$(find ~/.local/share/kstars/logs/ -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -f2- -d" ")
echo 'monitoring' $LATEST_LOG_FILE
tail -f $LATEST_LOG_FILE | grep 'Aborting\|ailed\|candidate job\|Scheduler: Find next job\|Scheduler:  \"Slewing to\|Target is within acceptable range\|Autofocus in progress\|Autofocus complete after\|Shutdown complete\|Roof is open\|Mount is parked\|unparked\|Parking mount\|Starting guiding procedure\|Scheduler: Get next action\|DEBG - Capture:  \"Received image \|Cant contact weather device\|bad weather\|severe weather' | while read line; do
    POST_MSG=$(eval echo $line | cut -d " " -f5-)
    curl -X POST -H 'Content-type: application/json' --data '{"text":"'"$POST_MSG"'"}' $WEBHOOK_URL
done