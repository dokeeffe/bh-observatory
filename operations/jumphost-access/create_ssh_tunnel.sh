#!/bin/bash
createTunnel() {
  /usr/bin/autossh -M 5122 -N -R 2345:localhost:22 dokeeffe@52-8.xyz
  if [[ $? -eq 0 ]]; then
    echo Tunnel to jumpbox created successfully
  else
    echo An error occurred creating a tunnel to jumpbox. RC was $?
  fi
}
/bin/pidof autossh
if [[ $? -ne 0 ]]; then
  echo Creating new tunnel connection
  createTunnel
fi

