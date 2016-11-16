#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyfirmata import Arduino, util
import pyfirmata
import time
from bottle import route, run, debug, error, abort

socket_to_relay_map = {'mount':7,'ccd':6,'filterwheel':5,'heaters':4,'focuser':3,'aux':2,'weatherstation':1}
socket_state_map = {'mount':'OFF','ccd':'OFF','filterwheel':'OFF','heaters':'OFF','focuser':'OFF','aux':'OFF','weatherstation':'OFF'}
valid_states = ['on','off']

@route('/power/<socket>/<state>')
def power_change_state(socket,state):
    if(state not in valid_states):
        abort(400, "Bad request. You need to specify the correct device and power state")
    command = state.upper() + str(socket_to_relay_map[socket])
    send_command(board,command)
    socket_state_map[socket] = state.upper()
    return socket_state_map

@route('/power')
def power_query():
    return socket_state_map

def send_command(board, cmd=[]):
    data = util.str_to_two_byte_iter(cmd+"\0")
    board.send_sysex(pyfirmata.pyfirmata.STRING_DATA, data)


board = Arduino('/dev/ttyUSB0')
run(host='0.0.0.0', port=8080)



