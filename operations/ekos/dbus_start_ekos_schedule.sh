#!/bin/bash

# TODO: Check observing conditions ok or not and exit or continue
# TODO: Check observing conditions ok or not and exit or continue

echo "Powering on all equipment"

if pgrep -x "indiserver" > /dev/null
then
    echo "indiserver Running"
else
    echo "Starting indiserver"
    sleep 2
fi

if pgrep -x "kstars" > /dev/null
then
    echo "kstars Running"
else
    echo "Starting kstars"
    nohup kstars > /dev/null 2>&1&
    sleep 10
fi

echo 'Loading EKOS Schedule file and starting scheduler'

dbus-send --session --print-reply --dest="org.kde.kstars" /kstars/MainWindow_1/actions/ekos org.qtproject.Qt.QAction.trigger
dbus-send --session --print-reply --dest="org.kde.kstars" /KStars/Ekos org.kde.kstars.Ekos.start
dbus-send --session --print-reply --dest="org.kde.kstars" /KStars/Ekos/Scheduler org.kde.kstars.Ekos.Scheduler.loadScheduler string:"/home/dokeeffe/Dropbox/EkosSchedules/AAVSO-Schedule.esl"
dbus-send --session --print-reply --dest="org.kde.kstars" /KStars/Ekos/Scheduler org.kde.kstars.Ekos.Scheduler.start

#TODO: Switch off IR lamps in camera
#TODO: Switch off Dehumidifier
#TODO: Send SMS