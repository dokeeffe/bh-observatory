#!/usr/bin/python

import requests

def main():
    requests.post(url='http://192.168.1.228:8080/abort')    
    print('OK')


if __name__ == "__main__":
    main()
