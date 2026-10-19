#!/usr/bin/python3
import json
import subprocess
import time
from datetime import datetime, timezone
import requests
from requests.adapters import HTTPAdapter, Retry


def wait_for_mount_to_stop_slewing():
    '''
    Wait for the mount to stop slewing before returning weather status. 
    This is a wokaround for a CEM120 driver bug where if PARK is sent to the mount while slewing, 
    it fails to park. This can cause the roof to close while the mount is unparked, 
    which can damage the mount and/or the roof.
    '''
    while True:
        try:
            result = subprocess.run(
                ['indi_getprop', 'iOptron CEM120.EQUATORIAL_EOD_COORD._STATE'],
                check=True,
                capture_output=True,
                text=True
            )
        except (OSError, subprocess.SubprocessError):
            return
        if 'Busy' not in result.stdout:
            return
        time.sleep(1)


def get_weather_status():
    s = requests.Session()
    retries = Retry(total=5,
                    backoff_factor=2,
                    status_forcelist=[ 500, 502, 503, 504 ])
    s.mount('http://', HTTPAdapter(max_retries=retries))
    weather_data = s.get('http://192.168.1.227:8080/weather/current')
    current_weather = weather_data.json()
    rain = current_weather['rain']
    sky_temp = current_weather['skyTemp']
    ambient_temp = current_weather['outsideTemp']
    clear = 1
    sky_temp_delta = current_weather['outsideTemp'] - current_weather['skyTemp']
    if rain:
        wait_for_mount_to_stop_slewing()
        clear = 0
        msg=f'Raining. sky:{sky_temp} ambient:{ambient_temp}'
    elif sky_temp_delta > 15 :
        clear = 1
        msg=f'Clear. sky:{sky_temp} ambient:{ambient_temp}'
    elif sky_temp_delta > 10:
        clear = 1
        msg=f'Partial Cloud. sky:{sky_temp} ambient:{ambient_temp}'
    else:
        wait_for_mount_to_stop_slewing()
        clear = 0
        msg=f'Cloudy!!!. sky:{sky_temp} ambient:{ambient_temp}'
    return clear, msg

def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")
    try:
        clear, msg = get_weather_status()
    except:
        clear = 3
        msg = 'System problem getting weather data'
    finally:
        print(json.dumps({"timestamp_utc": now,"roof_status": {"open_ok": clear,"reasons": msg}}))


if __name__ == '__main__':
    main()
