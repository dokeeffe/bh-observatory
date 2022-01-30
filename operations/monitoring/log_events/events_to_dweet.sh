#!/usr/bin/env bash

tail -f /home/dokeeffe/.local/share/kstars/logs/**/* | grep --line-buffered 'Aborting\|ailed\|candidate job\|Scheduler: Find next job\|Scheduler:  \"Slewing to\|Target is within acceptable range\|Autofocus in progress\|Autofocus complete after\|Shutdown complete\|Roof is open\|Mount is parked\|unparked\|Parking mount\|Starting guiding procedure\|Scheduler: Get next action\|bad weather\|severe weather\|Autofocus\|has completed\|estimated to take' | while read line; do
    POST_MSG=$(eval echo $line | cut -d " " -f6-)
    if [[ ! $POST_MSG == *"Cooling Info inquiry failed"* ]]; then
      echo $POST_MSG
      curl -X POST -H 'Content-type: application/json' --data '{"logline":"'"$POST_MSG"'"}' https://dweet.io/dweet/for/BobsLogs
    fi
done
