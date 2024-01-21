#!/bin/bash

autossh -M 0 -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" -N -f -R 13389:localhost:3389 dokeeffe@52-8.xyz

