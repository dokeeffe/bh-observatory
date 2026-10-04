#!/usr/bin/env python3
import json
import os
import subprocess

import boto3

OUTPUT_FILE = '/tmp/indi_properties.json'
R2_BUCKET = 'telemetry'
R2_OBJECT_KEY = 'indi_properties.json'


def get_indi_properties():
    """Call indi_getprop and return the text output."""
    try:
        result = subprocess.run(
            ['indi_getprop'],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            print(f'Error: indi_getprop returned code {result.returncode}')
            print(f'stderr: {result.stderr}')
            return None
        return result.stdout
    except FileNotFoundError:
        print('Error: indi_getprop command not found')
        return None
    except subprocess.TimeoutExpired:
        print('Error: indi_getprop timed out')
        return None


def parse_indi_text(text_output):
    """Parse INDI text output and convert to JSON structure.

    Format: device.property.element=value
    Example: iOptronV3.GPS_STATUS.On=Off
    """
    devices = {}

    for line in text_output.strip().split('\n'):
        line = line.strip()
        if not line or '=' not in line:
            continue

        path, value = line.split('=', 1)
        parts = path.split('.')

        if len(parts) < 3:
            continue

        device = parts[0]
        property_name = parts[1]
        element = '.'.join(parts[2:])

        if device not in devices:
            devices[device] = {}

        if property_name not in devices[device]:
            devices[device][property_name] = {}

        converted_value = convert_value(value)
        devices[device][property_name][element] = converted_value

    return devices


def convert_value(value):
    """Convert string value to appropriate type (number, boolean, or string)."""
    value = value.strip()

    try:
        if '.' in value:
            return float(value)
        return int(value)
    except ValueError:
        pass

    if value.lower() in ['on', 'off']:
        return value == 'On' or value == 'on'

    return value


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


def upload_state(local_path=OUTPUT_FILE, bucket_name=R2_BUCKET, object_key=R2_OBJECT_KEY):
    """Upload the JSON file to the configured R2 bucket."""
    try:
        client = get_r2_client()
        client.upload_file(local_path, bucket_name, object_key)
        return True
    except Exception as exc:
        print(f'Failed to upload indi properties to R2: {exc}')
        return False


def main():
    text_output = get_indi_properties() or ''
    json_data = parse_indi_text(text_output)
    if not json_data:
        print('No data parsed')
        json_data = {}

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as handle:
        json.dump(json_data, handle, indent=2)
        handle.write('\n')

    print(f'INDI properties saved to {OUTPUT_FILE}')
    print(f'Found {len(json_data)} devices')
    return 0 if upload_state() else 1


if __name__ == '__main__':
    raise SystemExit(main())

