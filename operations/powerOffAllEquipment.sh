#!/bin/bash
curl http://192.168.2.225:8080/power/ccd/off > /dev/null 2>&1
curl http://192.168.2.225:8080/power/filterwheel/off > /dev/null 2>&1
curl http://192.168.2.225:8080/power/mount/off > /dev/null 2>&1
curl http://192.168.2.225:8080/power/heaters/off > /dev/null 2>&1
curl http://192.168.2.225:8080/power/focuser/off > /dev/null 2>&1
curl http://192.168.2.225:8080/power/aux/off 


