#!/usr/bin/python3
import json
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter, Retry

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

    if rain:
        clear = 0
        msg=f'Raining. sky:{sky_temp} ambient:{ambient_temp}'
    elif current_weather['outsideTemp'] - current_weather['skyTemp'] > 15 :
        clear = 1
        msg=f'Clear. sky:{sky_temp} ambient:{ambient_temp}'
    else:
        clear=0
        msg=f'Cloudy. sky:{sky_temp} ambient:{ambient_temp}'
    return clear, msg

now=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S%z")
try:
    clear, msg = get_weather_status()
except:
    clear = 3
    msg = 'System problem getting weather data'
finally:
    print(json.dumps({"timestamp_utc": now,"roof_status": {"open_ok": clear,"reasons": msg}}))


