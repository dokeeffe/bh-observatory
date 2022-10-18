#!/usr/bin/python3

import requests
import time

def block_until(desired_state: str):
    for _ in range(20):
        time.sleep(1)
        resp = requests.get('http://192.168.1.228:8080/roof')
        if resp.json().get('state') == desired_state:
            return
    raise ValueError

def block_until_shutter_closed():
    for _ in range(30):
        time.sleep(1)
        resp = requests.get('http://192.168.1.228:8080/shutter')
        print(resp.json())
        if resp.json().get('state') == 'SHUTTERCLOSED':
            return

def main():
    requests.post(url='http://192.168.1.228:8080/shutterclose')
    #block_until_shutter_closed()
    time.sleep(25)
    requests.post(url='http://192.168.1.228:8080/close')    
    block_until('CLOSED')
    print('OK')


if __name__ == "__main__":
    main()
