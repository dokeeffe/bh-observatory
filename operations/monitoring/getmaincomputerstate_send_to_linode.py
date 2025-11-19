#!/usr/bin/env python3
import subprocess
import json
from datetime import datetime

def ping_host(hostname):
    """Ping a hostname and return True if online, False otherwise."""
    try:
        # Use -c 1 for one ping, -W 2 for 2 second timeout
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '2', hostname],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return result.returncode == 0
    except Exception:
        return False

def main():
    hostname = "main.local"
    is_online = ping_host(hostname)

    # Generate JSON data
    data = {
        "online": is_online,
        "timestamp": datetime.now().isoformat()
    }

    # Save to file
    with open('/tmp/pc_state.json', 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Status saved: {hostname} is {'online' if is_online else 'offline'}")

if __name__ == "__main__":
    main()
    subprocess.call(['scp', '/tmp/pc_state.json', 'dokeeffe@52-8.xyz:/var/www/html/images/telemetry/.'])
