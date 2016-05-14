#!/bin/bash

#
# Assuming the roof and scope are parked Just hibernate the scope and power off everyting
# TODO: Add a check for roof and scope and park both if not parked
#

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo $DIR
$DIR/nexstarHibernateAndPoweroff.sh 
sleep 30
echo 'Powering off all equipment'
$DIR/powerOffAllEquipment.sh 
echo 'Starting data reduction'
#TODO: spawn the data reduction process
echo 'Finished workflow'

exit 0
