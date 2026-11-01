#!/usr/bin/env python3
import ast
import os
import subprocess
import sys

import boto3

R2_BUCKET = 'telemetry'
OBJECTS = {
    'jsonJobs': ('ekos.json', 'string', 'application/json'),
    'logText': ('ekos_log.txt', 'string-list', 'text/plain; charset=utf-8'),
}
DBUS_DESTINATION = 'org.kde.kstars'
DBUS_OBJECT_PATH = '/KStars/Ekos/Scheduler'
DBUS_INTERFACE = 'org.kde.kstars.Ekos.Scheduler'
LOG_PATH = '/tmp/ekos-cron.log'


def log_error(message):
    with open(LOG_PATH, 'a', encoding='utf-8') as log:
        log.write(f'{message}\n')
    print(message, file=sys.stderr)


def get_kstars_bus_address():
    result = subprocess.run(
        ['pgrep', '-u', str(os.getuid()), '-x', 'kstars'],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 1:
        raise RuntimeError('KStars is not running')
    if result.returncode != 0:
        raise RuntimeError(f'pgrep failed: {result.stderr.strip()}')

    pid = result.stdout.splitlines()[0]
    with open(f'/proc/{pid}/environ', 'rb') as environ_file:
        environment = environ_file.read().split(b'\0')

    for entry in environment:
        key, separator, value = entry.partition(b'=')
        if separator and key == b'DBUS_SESSION_BUS_ADDRESS':
            address = value.decode()
            if address:
                return address
            break
    raise RuntimeError(f'Could not find DBus session address for KStars PID {pid}')


def get_dbus_property(bus_address, property_name, expected_type):
    result = subprocess.run(
        [
            '/usr/bin/gdbus',
            'call',
            '--session',
            '--dest',
            DBUS_DESTINATION,
            '--object-path',
            DBUS_OBJECT_PATH,
            '--method',
            'org.freedesktop.DBus.Properties.Get',
            DBUS_INTERFACE,
            property_name,
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
        env={**os.environ, 'DBUS_SESSION_BUS_ADDRESS': bus_address},
    )
    output = result.stdout.strip()
    if not output.startswith('(<') or not output.endswith('>,)'):
        raise RuntimeError(f'Unexpected DBus response for {property_name}: {output}')

    try:
        value = ast.literal_eval(output[2:-3])
    except (SyntaxError, ValueError) as error:
        raise RuntimeError(f'Could not parse DBus response for {property_name}: {error}') from error

    if expected_type == 'string' and isinstance(value, str):
        return value + '\n'
    if expected_type == 'string-list' and isinstance(value, list) and all(
        isinstance(line, str) for line in value
    ):
        return ''.join(f'{line}\n' for line in value)
    raise RuntimeError(f'Unexpected DBus value type for {property_name}')


def get_r2_client():
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


def main():
    try:
        bus_address = get_kstars_bus_address()
        payloads = {
            property_name: get_dbus_property(bus_address, property_name, expected_type)
            for property_name, (_, expected_type, _) in OBJECTS.items()
        }
        client = get_r2_client()
        for property_name, (object_key, _, content_type) in OBJECTS.items():
            client.put_object(
                Bucket=R2_BUCKET,
                Key=object_key,
                Body=payloads[property_name].encode('utf-8'),
                ContentType=content_type,
            )
            print(f'Uploaded {object_key} to R2 bucket {R2_BUCKET}')
    except Exception as error:
        log_error(f'Ekos monitor failed: {error}')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
