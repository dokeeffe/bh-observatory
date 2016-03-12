#!/bin/bash
die () {
    echo >&2 "$@"
    exit 1
}

[ "$#" -eq 1 ] || die "USAGE: ipCameraLight.sh <cmd> where cmd = ON or OFF"

if [ $1 == 'ON' ]
then
  echo 'Switching ON IR Lamps'
  curl 'http://52-8.xyz:8181/decoder_control.cgi?command=95' -H 'Authorization: Basic ZG9rZWVmZmU6ZG9rZWVmZmU='
fi

if [ $1 == 'OFF' ]
then
  echo 'Switching OFF IR Lamps'
  curl 'http://192.168.1.220/decoder_control.cgi?command=94' -H 'Authorization: Basic ZG9rZWVmZmU6ZG9rZWVmZmU='   
fi
