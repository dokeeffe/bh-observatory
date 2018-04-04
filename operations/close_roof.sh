#!/bin/bash

read -p "CLOSE ROOF. Are you sure y/n ? " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    indi_setprop 'Aldi Roof.CONNECTION.CONNECT=On'
    indi_setprop 'Aldi Roof.DOME_PARK.PARK=On'
fi

