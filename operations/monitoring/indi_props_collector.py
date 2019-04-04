#!/usr/bin/env python

import sys
import json
import subprocess
from subprocess import CalledProcessError

def get_indi_props(device):
    try:
        return subprocess.check_output(['indi_getprop', device])
    except CalledProcessError as e:
        sys.exit(1)

def add_props_to_dict(props, dict):
    if props is not None:
        for line in props.split('\n'):
            if '=' in line:
                key, val = line.split('=')
                dict[key] = val;

dict = {}
add_props_to_dict(get_indi_props('Aldi Roof.*.*'), dict)
add_props_to_dict(get_indi_props('Celestron AuxRemote Gateway.*.*'), dict)
print(json.dumps(dict, sort_keys=True, indent=4, separators=(',', ': ')))
