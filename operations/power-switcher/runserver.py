#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyfirmata import Arduino, util
import pyfirmata
import bottle
from bottle import route, run, debug, error, abort, template, response

socket_to_relay_map = {'mount':5,'ccd':7,'filterwheel':6,'heaters':4,'focuser':2,'aux':3,'weatherstation':1}
socket_state_map = {'mount':'OFF','ccd':'OFF','filterwheel':'OFF','heaters':'OFF','focuser':'OFF','aux':'OFF','weatherstation':'ON'}
valid_states = ['on','off']

@route('/power/<socket>/<state>')
def power_change_state(socket,state):
    if(state not in valid_states):
        abort(400, "Bad request. You need to specify the correct device and power state")
    if(socket == 'weatherstation'):
        state = flip_state(state)
    command = state.upper() + str(socket_to_relay_map[socket])
    send_arduino_command(board, command)
    socket_state_map[socket] = state.upper()
    return socket_state_map

@route('/power')
def power_query():
    return socket_state_map

@route('/')
def index():
    return template('index_template')

def flip_state(state):
    if(state == 'on'):
        return 'off'
    elif(state == 'off'):
        return 'on'

def send_arduino_command(board, cmd=[]):
    data = util.str_to_two_byte_iter(cmd+"\0")
    board.send_sysex(pyfirmata.pyfirmata.STRING_DATA, data)

def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

        if bottle.request.method != 'OPTIONS':
            # actual request; reply with the actual response
            return fn(*args, **kwargs)

    return _enable_cors



board = Arduino('/dev/ttyUSB0')
run(host='0.0.0.0', port=8080)