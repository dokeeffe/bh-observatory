import os
import ConfigParser
import imageCollectionUtils
import logging

from astropy import units as u

import ccdproc
from ccdproc import CCDData
from ccdproc import ImageFileCollection

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
    indir = config.get('Dark_Paths', 'rawdir')
    bias_dir = config.get('Bias_Paths', 'masterdir')
    outdir = config.get('Dark_Paths', 'masterdir')

    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    os.chdir(outdir)
    dark_ic = ImageFileCollection(indir)
    bias_ic = ImageFileCollection(bias_dir)

    # collect the raw darks and collate by time, binning and temp, subtract appropriate Bias while collecting.
    darks = {}
    for filename in dark_ic.files_filtered(FRAME='Dark'):
        dark_ccd = CCDData.read(dark_ic.location + filename, unit=u.adu)
        dark_key = imageCollectionUtils.generate_dark_key(dark_ccd)
        if dark_key not in darks:
            darks[dark_key] = []
        logging.info('Performing Bias subtraction')
        bias_corrected = imageCollectionUtils.subtract_best_bias_temp_match(bias_ic,dark_ccd)
        darks[dark_key].append(bias_corrected)
    logging.info('Dark frames collected and collated by time,temperature and binning. Performing median combination')
    imageCollectionUtils.combine_values_from_dictionary_and_write(darks, 'master_dark', 'average')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    generate_darks()
