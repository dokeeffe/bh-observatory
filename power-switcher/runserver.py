#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyfirmata
from bottle import route, run, abort, template
from pyfirmata import Arduino, util

socket_to_relay_map = {'mount': 5, 'ccd': 7, 'filterwheel': 6, 'heaters': 4, 'focuser': 2, 'aux': 3,
                       'weatherstation': 1, 'mainsplug': 8}
socket_state_map = {'mount': 'OFF', 'ccd': 'OFF', 'filterwheel': 'OFF', 'heaters': 'OFF', 'focuser': 'OFF',
                    'aux': 'OFF', 'weatherstation': 'ON', 'mainsplug': 'ON'}
valid_states = ['on', 'off']


@route('/power/<socket>/<state>')
def power_change_state(socket, state):
    '''
    Handle request to change power state for a socket. Example '/power/mount/on'
    :param socket:
    :param state:
    :return:
    '''
    if state not in valid_states:
        abort(400, "Bad request. You need to specify the correct device and power state")
    command = state.upper() + str(socket_to_relay_map[socket])
    if socket == 'weatherstation' or socket == 'mainsplug':
        # We need to flip the on/off states for the weather station and mains as its wired to a normally closed relay (off=on and on=off for that relay)
        command = flip_state(state).upper() + str(socket_to_relay_map[socket])
    send_arduino_command(board, command)
    socket_state_map[socket] = state.upper()
    return socket_state_map


@route('/power')
def power_query():
    '''
    Handle request to get the current state of all power switches
    :return:
    '''
    return socket_state_map


@route('/')
def index():
    '''
    index will respond with the *very basic* UI web page
    :return:
    '''
    return template('index_template')


def flip_state(state):
    '''
    Flip on to off and off to on. must be a better way to do this
    :param state:
    :return:
    '''
    return 'off' if state == 'on' else 'on'


def send_arduino_command(board, cmd=[]):
    '''
    Send the command to the arduino to set relay state
    :param board:
    :param cmd:
    :return:
    '''
    data = util.str_to_two_byte_iter(cmd + "\0")
    board.send_sysex(pyfirmata.pyfirmata.STRING_DATA, data)


board = Arduino('/dev/ttyUSB0')
run(host='0.0.0.0', port=8080)
