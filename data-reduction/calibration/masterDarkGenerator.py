import ConfigParser
import json
import logging
import os
from astropy import units as u

from ccdproc import CCDData
from ccdproc import ImageFileCollection

import calibrationUtils


#
# This script is responsible for generation of master darks. Darks are created by median combination
# of frames grouped by time,binning and temperature
# Calibration logic is based on AAVSO guidelines from their CCDPhotometryGuide.pdf
#     Take 20 or more images, subtract the Master Bias from each,
#     then median combine them all together to create a Master Dark
# This is performed for all raw dark frames grouped by time, binning and sensor temperature.
#
def generate_darks():
    config = ConfigParser.ConfigParser()
    config.read('calibration.cfg')
    combine_method = config.get('Flat_Paths', 'combine_method')
    outdir = config.get('Dark_Paths', 'masterdir')
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    os.chdir(outdir)
    master_bias_ic = ImageFileCollection(config.get('Bias_Paths', 'masterdir'))
    rawdirs_to_process = json.loads(config.get('Dark_Paths', 'rawdirs'))
    for rawdir_to_process in rawdirs_to_process:
        dark_ic = ImageFileCollection(rawdir_to_process)
        if not dark_ic.files:
            logging.warn('no data in ' + rawdir_to_process)
        else:
            logging.info('processing raw dir ' + rawdir_to_process)
            # collect the raw darks and collate by time, binning and temp, subtract appropriate Bias while collecting.
            darks = {}
            for filename in dark_ic.files_filtered(FRAME='Dark'):
                dark_ccd = CCDData.read(dark_ic.location + filename, unit=u.adu)
                dark_key = calibrationUtils.generate_dark_key(dark_ccd)
                if dark_key not in darks:
                    darks[dark_key] = []
                logging.info('Performing Bias subtraction')
                bias_corrected = calibrationUtils.subtract_best_bias_temp_match(master_bias_ic, dark_ccd)
                darks[dark_key].append(bias_corrected)
            logging.info('Dark frames collected and collated by time,temperature and binning. Performing median combination and save')
            calibrationUtils.combine_values_from_dictionary_and_write(darks, 'master_dark', combine_method)
            logging.info('Master Dark generated, proceeding to archive the raw files')
            calibrationUtils.move_to_archive(rawdir_to_process, dark_ic.files_filtered(FRAME='Dark'),prefix='raw_dark_data_')
            logging.info('Completed archival of raw dark data')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    generate_darks()
