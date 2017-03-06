#!/bin/bash

echo 'Loading EKOS Schedule file and starting scheduler'

dbus-send --session --print-reply --dest="org.kde.kstars" /kstars/MainWindow_1/actions/ekos org.qtproject.Qt.QAction.trigger
dbus-send --session --print-reply --dest="org.kde.kstars" /KStars/Ekos/Scheduler org.kde.kstars.Ekos.Scheduler.loadScheduler string:"/home/dokeeffe/Dropbox/EkosSchedules/GeneratedSchedule.esl"
dbus-send --session --print-reply --dest="org.kde.kstars" /KStars/Ekos/Scheduler org.kde.kstars.Ekos.Scheduler.start
