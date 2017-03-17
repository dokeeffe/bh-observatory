#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import call

import pyfirmata
from bottle import route, run, abort, template
from pyfirmata import Arduino, util

socket_to_relay_map = {'mount': 5, 'ccd': 7, 'filterwheel': 6, 'heaters': 4, 'focuser': 2, 'aux': 3,
                       'weatherstation': 1}
socket_state_map = {'mount': 'OFF', 'ccd': 'OFF', 'filterwheel': 'OFF', 'heaters': 'OFF', 'focuser': 'OFF',
                    'aux': 'OFF', 'weatherstation': 'ON'}
valid_states = ['on', 'off']


@route('/power/<socket>/<state>')
def power_change_state(socket, state):
    if (state not in valid_states):
        abort(400, "Bad request. You need to specify the correct device and power state")
    command = state.upper() + str(socket_to_relay_map[socket])
    if (socket == 'weatherstation'):
        # We need to flip the on/off states for the weather station as its wired to a normally closed relay (off=on and on=off for that relay)
        command = flip_state(state).upper() + str(socket_to_relay_map[socket])
    send_arduino_command(board, command)
    socket_state_map[socket] = state.upper()
    return socket_state_map


@route('/power')
def power_query():
    return socket_state_map


@route('/pc/wake')
def wake_pc():
    call(['wakeonlan', 'b4:b5:2f:cd:bd:05'])
    return {'wake': 'OK'}


@route('/')
def index():
    return template('index_template')


def flip_state(state):
    if (state == 'on'):
        return 'off'
    elif (state == 'off'):
        return 'on'


def send_arduino_command(board, cmd=[]):
    data = util.str_to_two_byte_iter(cmd + "\0")
    board.send_sysex(pyfirmata.pyfirmata.STRING_DATA, data)


board = Arduino('/dev/ttyUSB0')
run(host='0.0.0.0', port=8080)
