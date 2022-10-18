#!/usr/bin/python

import ConfigParser
import json
import logging
import os
from astropy import log as astropylog
from astropy import units as u

from ccdproc import CCDData
from ccdproc import ImageFileCollection

import calibrationUtils


def fix_filter_headers():
    config = ConfigParser.ConfigParser()
    config.read('calibration.cfg')
    outdir = config.get('Light_Path', 'masterdir')
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    os.chdir(outdir)
    master_bias_ic = ImageFileCollection(config.get('Bias_Paths', 'masterdir'))
    master_dark_ic = ImageFileCollection(config.get('Dark_Paths', 'masterdir'))
    master_flat_ic = ImageFileCollection(config.get('Flat_Paths', 'masterdir'))
    rawdirs_to_process = calibrationUtils.find_dirs_containing_fits_files(config.get('Light_Path', 'rawdir'))
    for rawdir_to_process in rawdirs_to_process:
        light_ic = ImageFileCollection(rawdir_to_process)
        if not light_ic.files:
            logging.warn('no data in ' + rawdir_to_process)
        else:
            files_to_archive = []
            # collect the raw light frames and collate by time, binning and temp, subtract appropriate Bias while collecting.
            for filename in light_ic.files_filtered(FRAME='Light'):
                filename_full_path = os.path.join(light_ic.location,filename)
                light_ccd = CCDData.read(filename_full_path, unit=u.adu)
                if 'FILTER' not in light_ccd.header:
                    logging.warning('filter missing from fits header {}'.format(filename_full_path))
                    filter = os.path.basename(os.path.dirname(filename_full_path))
                    print(filter)
                    light_ccd.header['FILTER'] = filter 


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    astropylog.setLevel('WARNING')
    fix_filter_headers()
