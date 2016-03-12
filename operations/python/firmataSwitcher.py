#! /usr/bin/env python

"""pyduino - A python library to interface with the firmata arduino firmware.
Copyright (C) 2007 Joe Turner <orphansandoligarchs@gmail.com>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import pyduino
import sys
import time

def usage():
    print """Usage: ./example.py port mode 
Available modes: 1 - All off
                 2 - All on"""

if __name__ == "__main__":
    try:
        arduino = pyduino.Arduino(sys.argv[1])
        mode = int(sys.argv[2])
    except IndexError, ValueError:
        usage()
        sys.exit()
    if mode == 1:
        for num in range(2,6):
            arduino.digital[num].set_active(1)
            arduino.digital[num].set_mode(pyduino.DIGITAL_OUTPUT)
            arduino.digital[num].write(0)    #Turn output low
    if mode == 2:
        for num in range(2,6):
            arduino.digital[num].set_active(1)
            arduino.digital[num].set_mode(pyduino.DIGITAL_OUTPUT)
            arduino.digital[num].write(1)    #Turn output high
    #Not sure we have to write so many times, firmata sucks! Send the same message 300times to the arduino to switch the pins on.
    for loop in range(0,300):
        try:
            arduino.iterate()
            if mode == 2:
                for num in range(2,6):    
		    high = 1
	            arduino.digital[num].set_active(1)
            	    arduino.digital[num].set_mode(pyduino.DIGITAL_OUTPUT)
                    arduino.digital[num].write(high)
        except KeyboardInterrupt:
            break

