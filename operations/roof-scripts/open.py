#!/usr/bin/python

import requests
import time

def block_until(desired_state: str):
    for _ in range(20):
        time.sleep(1)
        resp = requests.get('http://192.168.1.228:8080/roof')
        if resp.json().get('state') == desired_state:
            return
    raise ValueError

def main():
    requests.post(url='http://192.168.1.228:8080/open')    
    block_until('OPEN')    
    print('OK')
    

if __name__ == "__main__":
    main()
