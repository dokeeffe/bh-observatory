#!/usr/bin/python3
import logging
from astropy.io import fits
import os
import fnmatch
import re
import datetime


def safe_filename(s):
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


def convert_datetime(s):
    date_time_obj = datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%f')
    return date_time_obj.strftime('%Y-%m-%d-%H-%M-%S')


def add_fits_object_to_filename():
    for root, dirnames, filenames in os.walk('/home/dokeeffe/Pictures/CalibratedLight'):
        for filename in fnmatch.filter(filenames, '*.fits'):
            try:
                hdu = fits.open(os.path.join(root, filename))
                if 'OBJECT' in hdu[0].header:
                    obj_name = safe_filename(hdu[0].header['OBJECT'])
                    filter = safe_filename(
                        hdu[0].header['FILTER']) if 'filter' in hdu[0].header else '-'
                    if not filename.startswith(obj_name) or not filter in filename:
                        date_obs = convert_datetime(hdu[0].header['DATE-OBS'])
                        new_name = '{}--{}--{}--Light{}'.format(
                            obj_name, date_obs, filter, filename.split('Light')[1])
                        print('renaming {} to {}'.format(filename, new_name))
                        os.rename(os.path.join(root, filename),
                                  os.path.join(root, new_name))
                else:
                    print(f'OBJECT missing from fits header {filename}')
            except:
                print('ERROR: could not open {}'.format(filename))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    add_fits_object_to_filename()
