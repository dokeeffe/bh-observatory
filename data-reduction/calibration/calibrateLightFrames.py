import ConfigParser
import json
import logging
import os
from astropy import log as astropylog
from astropy import units as u

from ccdproc import CCDData
from ccdproc import ImageFileCollection

import imageCollectionUtils


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
    outdir = config.get('Light_Paths', 'masterdir')
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    os.chdir(outdir)
    master_bias_ic = ImageFileCollection(config.get('Bias_Paths', 'masterdir'))
    master_dark_ic = ImageFileCollection(config.get('Dark_Paths', 'masterdir'))
    master_flat_ic = ImageFileCollection(config.get('Flat_Paths', 'masterdir'))
    rawdirs_to_process = json.loads(config.get('Light_Paths', 'rawdirs'))
    for rawdir_to_process in rawdirs_to_process:
        logging.info('processing raw dir ' + rawdir_to_process)
        light_ic = ImageFileCollection(rawdir_to_process)

        # collect the raw light frames and collate by time, binning and temp, subtract appropriate Bias while collecting.
        for filename in light_ic.files_filtered(FRAME='Light'):
            light_ccd = CCDData.read(light_ic.location + filename, unit=u.adu)
            logging.info('Bias correcting ' + filename)
            bias_corrected = imageCollectionUtils.subtract_best_bias_temp_match(master_bias_ic,light_ccd)
            logging.info('Dark correcting ' + filename)
            dark_corrected = imageCollectionUtils.subtract_best_dark(master_dark_ic,bias_corrected)
            logging.info('Flat correcting ' + filename)
            flat_corrected = imageCollectionUtils.flat_correct(master_flat_ic,dark_corrected)
            # generate a date based dir and write callibrated data
            date_dir = imageCollectionUtils.extract_date_from(flat_corrected)
            if not os.path.isdir(outdir+date_dir):
                os.mkdir(outdir+date_dir)
            os.chdir(outdir+date_dir)
            date_file_prefix  = imageCollectionUtils.extract_datetime_from(flat_corrected)
            flat_corrected.write(date_file_prefix + filename, clobber=True)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    astropylog.setLevel('WARNING')
    calibrate_light()
