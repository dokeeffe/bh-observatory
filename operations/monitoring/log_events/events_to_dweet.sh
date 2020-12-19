#!/usr/bin/env bash

tail -f /home/dokeeffe/.local/share/kstars/logs/**/* | grep --line-buffered 'Aborting\|ailed\|candidate job\|Scheduler: Find next job\|Scheduler:  \"Slewing to\|Target is within acceptable range\|Autofocus in progress\|Autofocus complete after\|Shutdown complete\|Roof is open\|Mount is parked\|unparked\|Parking mount\|Starting guiding procedure\|Scheduler: Get next action\|DEBG - Capture:  \"Received image \|Cant contact weather device\|bad weather\|severe weather' | while read line; do
    POST_MSG=$(eval echo $line | cut -d " " -f6-)
    echo $POST_MSG
    curl -X POST -H 'Content-type: application/json' --data '{"logline":"'"$POST_MSG"'"}' https://dweet.io/dweet/for/BobsLogs
done
