#!/usr/bin/env python3
import json
import os
import socket
from datetime import datetime, timezone

import boto3

STATE_PATH = '/tmp/pc_state.json'
R2_BUCKET = 'telemetry'


def get_uptime():
    """Get system uptime in seconds."""
    try:
        with open('/proc/uptime', 'r', encoding='utf-8') as handle:
            return float(handle.read().split()[0])
    except Exception as exc:  # pragma: no cover - defensive logging only
        print(f'Error reading uptime: {exc}')
        return None


def get_load_average():
    """Get system load averages for 1, 5, and 15 minutes."""
    try:
        with open('/proc/loadavg', 'r', encoding='utf-8') as handle:
            load_avg = handle.read().split()[:3]
        return {
            '1min': float(load_avg[0]),
            '5min': float(load_avg[1]),
            '15min': float(load_avg[2]),
        }
    except Exception as exc:  # pragma: no cover - defensive logging only
        print(f'Error reading load average: {exc}')
        return None


def build_state():
    """Build a JSON-serialisable system status dictionary."""
    return {
        'online': True,
        'hostname': socket.gethostname(),
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'uptime_seconds': get_uptime(),
        'load_average': get_load_average(),
    }


def write_state(path=STATE_PATH, data=None):
    """Persist system state to a local JSON file."""
    if data is None:
        data = build_state()
    with open(path, 'w', encoding='utf-8') as handle:
        json.dump(data, handle, indent=2)
        handle.write('\n')
    return path


def get_r2_client():
    """Create an S3-compatible client for Cloudflare R2."""
    required_vars = {
        'CLOUDFLARE_R2_ACCESS_KEY_ID': os.environ.get('CLOUDFLARE_R2_ACCESS_KEY_ID'),
        'CLOUDFLARE_R2_SECRET': os.environ.get('CLOUDFLARE_R2_SECRET'),
        'CLOUDFLARE_R2_ENDPOINT': os.environ.get('CLOUDFLARE_R2_ENDPOINT'),
    }

    missing = [name for name, value in required_vars.items() if not value]
    if missing:
        raise RuntimeError(f'Missing required R2 environment variables: {", ".join(missing)}')

    return boto3.client(
        's3',
        endpoint_url=required_vars['CLOUDFLARE_R2_ENDPOINT'],
        aws_access_key_id=required_vars['CLOUDFLARE_R2_ACCESS_KEY_ID'],
        aws_secret_access_key=required_vars['CLOUDFLARE_R2_SECRET'],
        region_name='auto',
    )


def upload_state(local_path=STATE_PATH, bucket_name=R2_BUCKET, object_key='pc_state.json'):
    """Upload the local state file to the configured R2 bucket."""
    try:
        client = get_r2_client()
        client.upload_file(local_path, bucket_name, object_key)
        return True
    except Exception as exc:
        print(f'Failed to upload pc state to R2: {exc}')
        return False


def main():
    data = build_state()
    write_state(data=data)
    return 0 if upload_state() else 1


if __name__ == '__main__':
    raise SystemExit(main())
