#!/usr/bin/env python3
import json
import subprocess
from datetime import datetime

def main():
    # Generate JSON data
    data = {
        "online": True,
        "timestamp": datetime.now().isoformat()
    }

    # Save to file
    with open('/tmp/pc_state.json', 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    main()
    subprocess.call(['scp', '/tmp/pc_state.json', 'dokeeffe@52-8.xyz:/var/www/html/images/telemetry/.'])
