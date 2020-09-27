#!/usr/bin/python

from astropy.io import fits
import json
import re
import os
import fnmatch
import zipfile
from shutil import copyfile
from shutil import rmtree

REGENERATE_ZIPS = False

def attempt_extract_object_name_from_filename(filename):
    parts = filename.split('_')
    if len(parts) == 1:
        return 'Unknown'
    try:
        result = re.split(r'(([0-9][0-9][0-9][0-9])-([0-9][0-9])-([0-9][0-9])-([0-9][0-9])-([0-9][0-9])-([0-9][0-9]))', filename)[-1].split('_')[0]
        if result == 'Light':
            return 'Unknown'
        return result
    except:
        return 'Unknown'

def build_dict_of_objects(path):
    print('Scanning fits files')
    result = {}
    rmtree('/tmp/solver', ignore_errors=True)
    os.mkdir('/tmp/solver')
    for root, dirnames, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, '*.fits'):
            fullpath = os.path.join(root, filename)
            hdu = fits.open(fullpath)
            header = hdu[0].header
            object = header['OBJECT'] if 'OBJECT' in header else attempt_extract_object_name_from_filename(filename)
            if object not in result:
               result[object] = []
            result[object].append({'filename': filename, 'path': fullpath, 'thumbnail':filename.replace('.fits','.jpeg')})
    return result

def build_zip_path(filename):
    return '/home/dokeeffe/pCloudDrive/Public Folder/{}.zip'.format(re.sub(r'[^\w\d-]','_',filename))

def build_pcloud_link(filename):
    return 'https://filedn.com/lARtHI6fhPgy6yeq3DqQev4/{}.zip'.format(re.sub(r'[^\w\d-]','_',filename))

def write_zip_files_per_object(objects):
    print('Generating zips grouped by object')
    for key, val in objects.items():
        paths = [filedetails['path'] for filedetails in val]
        if not os.path.exists(build_zip_path(key)) or REGENERATE_ZIPS:
            ZipFile = zipfile.ZipFile(build_zip_path(key), 'w', allowZip64=True)
            for fits in paths:
                print('adding {} to zip'.format(os.path.basename(fits)))
                ZipFile.write(fits, os.path.basename(fits), compress_type=zipfile.ZIP_DEFLATED)
        else:
            print('ZIP exists, skipping')

def write_summary_json(objects):
    result_array = []
    for key, val in objects.items():
        result_array.append({'name': key, 'filecount': len(val), 'link': build_pcloud_link(key), 'files': val})
    with open('fits_data_extract.json', 'w') as outfile:
        json.dump(result_array, outfile)


if __name__ == "__main__":
    objects = build_dict_of_objects('/home/dokeeffe/Pictures/CalibratedLight')
    write_zip_files_per_object(objects)
    write_summary_json(objects)
