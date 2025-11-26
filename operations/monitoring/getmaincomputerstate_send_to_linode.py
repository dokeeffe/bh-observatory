#!/usr/bin/env python3
import json
import subprocess
from datetime import datetime

def get_uptime():
    """Get system uptime in seconds"""
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.read().split()[0])
        return uptime_seconds
    except Exception as e:
        print(f"Error reading uptime: {e}")
        return None

def get_load_average():
    """Get system load average (1, 5, 15 minutes)"""
    try:
        with open('/proc/loadavg', 'r') as f:
            load_avg = f.read().split()[:3]
        return {
            "1min": float(load_avg[0]),
            "5min": float(load_avg[1]),
            "15min": float(load_avg[2])
        }
    except Exception as e:
        print(f"Error reading load average: {e}")
        return None

def main():
    # Generate JSON data
    data = {
        "online": True,
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": get_uptime(),
        "load_average": get_load_average()
    }

    # Save to file
    with open('/tmp/pc_state.json', 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    main()
    subprocess.call(['scp', '/tmp/pc_state.json', 'dokeeffe@52-8.xyz:/var/www/html/images/telemetry/.'])
