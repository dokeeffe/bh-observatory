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


# This script is used to calibrate 'Light' frames containing astronomical data.
# It performs bias correction, flat division, and flat correction.
# It will auto locate the correct bias, dark and flat based on binning, temp, exposure and filter.
# Assumes all master bias,dark,and flats are already generated and located in one dir.
#
# Calibration logic is based on AAVSO guidelines from their CCDPhotometryGuide.pdf
#
def calibrate_light():


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
    print(rawdirs_to_process)
    for rawdir_to_process in rawdirs_to_process:
        light_ic = ImageFileCollection(rawdir_to_process)
        if not light_ic.files:
            logging.warn('no data in ' + rawdir_to_process)
        else:
            logging.info('processing raw dir ' + rawdir_to_process)
            files_to_archive = []
            # collect the raw light frames and collate by time, binning and temp, subtract appropriate Bias while collecting.
            for filename in light_ic.files_filtered(FRAME='Light'):
                filename_full_path = os.path.join(light_ic.location,filename)
                light_ccd = CCDData.read(filename_full_path, unit=u.adu)
                logging.info('Calibrating {}'.format(filename_full_path))
                logging.info('    RES: {} x {} FILTER: {}'.format(light_ccd.header['NAXIS1'], light_ccd.header['NAXIS2'], light_ccd.header['FILTER']))
                logging.info('    Bias correcting {}'.format(filename))
                bias_corrected = calibrationUtils.subtract_best_bias_temp_match(master_bias_ic, light_ccd)
                logging.info('    Dark correcting {}'.format(filename))
                dark_corrected = calibrationUtils.subtract_best_dark(master_dark_ic, bias_corrected)
                logging.info('    Flat correcting {}'.format(filename))
                flat_corrected = calibrationUtils.flat_correct(master_flat_ic, dark_corrected)
                # generate a date based dir and write callibrated data into the configured masterdir
                date_dir = calibrationUtils.extract_date_from(flat_corrected)
                logging.info('generating a date based dir {} to write callibrated data into {}'.format(date_dir, outdir))
                if not os.path.isdir(outdir+date_dir):
                    os.mkdir(outdir+date_dir)
                os.chdir(outdir+date_dir)
                date_file_prefix  = calibrationUtils.extract_datetime_from(flat_corrected)
                flat_corrected.write(date_file_prefix + filename, clobber=True)
                logging.info('Written calibrated LIGHT {}\n\n\n'.format(date_file_prefix + filename))
                files_to_archive.append(filename)
            calibrationUtils.move_to_archive(rawdir_to_process, files_to_archive)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    astropylog.setLevel('WARNING')
    calibrate_light()
