#!/usr/bin/env python3
import json
import os
from datetime import datetime
import urllib.request

import boto3

CURRENT_FILE = '/tmp/roof.json'
REMOTE_FILE = '/tmp/roof_new.json'
R2_BUCKET = 'telemetry'
R2_OBJECT_KEY = 'roof.json'
ROOF_URL = 'http://localhost:8080/roof'


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


def upload_file(local_path=CURRENT_FILE, bucket_name=R2_BUCKET, object_key=R2_OBJECT_KEY):
    """Upload the roof state JSON to the configured R2 bucket."""
    try:
        get_r2_client().upload_file(local_path, bucket_name, object_key)
        return True
    except Exception as exc:
        print(f'Failed to upload roof state to R2: {exc}')
        return False


def main():
    urllib.request.urlretrieve(ROOF_URL, REMOTE_FILE)

    with open(REMOTE_FILE, 'r', encoding='utf-8') as handle:
        new_data = json.load(handle)

    if os.path.exists(CURRENT_FILE):
        with open(CURRENT_FILE, 'r', encoding='utf-8') as handle:
            old_data = json.load(handle)

        if old_data.get('state') != new_data.get('state'):
            new_data['last_changed'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        else:
            new_data['last_changed'] = old_data.get(
                'last_changed',
                datetime.now().strftime('%Y-%m-%d %H:%M'),
            )
    else:
        new_data['last_changed'] = datetime.now().strftime('%Y-%m-%d %H:%M')

    with open(CURRENT_FILE, 'w', encoding='utf-8') as handle:
        json.dump(new_data, handle)
        handle.write('\n')

    return 0 if upload_file() else 1


if __name__ == '__main__':
    raise SystemExit(main())
