#!/usr/bin/env python3
import gzip
import os
import shutil
import urllib.request

import boto3

OUTPUT_FILE = '/tmp/weather-history.json'
GZIP_FILE = '/tmp/weather-history.json.gz'
R2_BUCKET = 'telemetry'
R2_OBJECT_KEY = 'weather-history.json'
WEATHER_URL = 'http://192.168.1.227:8080/weather/history'


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


def upload_file(local_path=OUTPUT_FILE, bucket_name=R2_BUCKET, object_key=R2_OBJECT_KEY):
    """Gzip and upload the weather history JSON to the configured R2 bucket."""
    try:
        with open(local_path, 'rb') as source:
            with gzip.open(GZIP_FILE, 'wb') as compressed:
                shutil.copyfileobj(source, compressed)

        get_r2_client().upload_file(
            GZIP_FILE,
            bucket_name,
            object_key,
            ExtraArgs={
                'ContentType': 'application/json',
                'ContentEncoding': 'gzip',
            },
        )
        return True
    except Exception as exc:
        print(f'Failed to upload weather history to R2: {exc}')
        return False


def main():
    urllib.request.urlretrieve(WEATHER_URL, OUTPUT_FILE)
    return 0 if upload_file() else 1


if __name__ == '__main__':
    raise SystemExit(main())
