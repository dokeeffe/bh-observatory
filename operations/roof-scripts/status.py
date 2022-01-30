#!/usr/bin/python3

import sys
import requests

OPEN='0 1 0'
CLOSED='1 0 0'
UNKNOWN='2 0 0'

def query_roof():
    resp = requests.get(url='http://192.168.1.228:8080/roof')
    return resp.json()['state'] 
    

def write_to_indi_tempfile(path, state):
    status_file = open(path, 'w')
    status_file.truncate()
    if state=='OPEN':
        status_file.write(OPEN)
    elif state=='CLOSED':
        status_file.write(CLOSED)
    elif state=='UNKNOWN':
        status_file.write(UNKNOWN)
    status_file.close()


def main(path):
    '''
    Queries the roof and writes a 3 digit string to the temp file passed. 3 digits represent park-state, shutter state and azimuth.
    Since this is not a rotating dome, the azimuth is hard coded to 0.
    '''
    state = query_roof()
    write_to_indi_tempfile(path, state)


if __name__ == "__main__":
    script, path = sys.argv
    main(path)
