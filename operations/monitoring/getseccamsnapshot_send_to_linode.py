#!/usr/bin/env python3
import os
import requests
import shutil
import subprocess
import re

import boto3

R2_BUCKET = 'telemetry'


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


def upload_file(local_path, object_key, bucket_name=R2_BUCKET):
    """Upload a camera snapshot to the configured R2 bucket."""
    try:
        get_r2_client().upload_file(local_path, bucket_name, object_key)
        return True
    except Exception as exc:
        print(f'Failed to upload {object_key} to R2: {exc}')
        return False


def get_cam_ip(name):
    output = subprocess.check_output(f'/usr/local/bin/foscam-search-tool | grep {name}', shell=True, text=True)
    ip_address = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", output)
    if ip_address:
        ip_address = ip_address.group(0)
    else:
        ip_address = None
    print(f'found camera {ip_address}')
    return ip_address

def take_snapshot(cam_ip_address, name, ath):
    img_url= f'http://{cam_ip_address}:88/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr=dokeeffe&pwd={ath}'
    print(f'{img_url}')
    response = requests.get(img_url, stream=True)
    with open(f'/tmp/snapshot-{name}.jpg', 'wb') as fout:
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, fout)



def main():
    take_snapshot(get_cam_ip('Observatory'), 'obs1', 'Doohan21*')
    obs1_uploaded = upload_file('/tmp/snapshot-obs1.jpg', 'snapshot-obs1.jpg')

    take_snapshot(get_cam_ip('obs2'), 'obs2', 'zxcvbn3')
    obs2_uploaded = upload_file('/tmp/snapshot-obs2.jpg', 'snapshot-obs2.jpg')

    return 0 if obs1_uploaded and obs2_uploaded else 1


if __name__ == '__main__':
    raise SystemExit(main())
