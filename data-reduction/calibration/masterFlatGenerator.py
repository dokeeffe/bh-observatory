import ConfigParser
import json
import logging
import os

import ccdproc
from ccdproc import ImageFileCollection

import imageCollectionUtils


#
# This script is responsible for generation of master flats from a directory containing flat frames.
# Calibration logic is based on AAVSO guidelines from their CCDPhotometryGuide.pdf and is as follows:
#      Take 10 or more images for each filter, average (or median combine) them together, then
#      subtract the Master Dark and Master Bias to create a Master Flat.
#
def generate_flats():
    config = ConfigParser.ConfigParser()
    config.read('calibration.cfg')
    outdir = config.get('Flat_Paths', 'masterdir')
    combine_method = config.get('Flat_Paths', 'combine_method')
    master_bias_ic = ImageFileCollection(config.get('Bias_Paths', 'masterdir'))
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    os.chdir(outdir)
    rawdirs_to_process = json.loads(config.get('Flat_Paths', 'rawdirs'))
    for rawdir_to_process in rawdirs_to_process:
        logging.info('processing raw dir ' + rawdir_to_process)
        flat_ic = ImageFileCollection(rawdir_to_process)
        # collect the raw flats in a dictionary and collate by filter and binning
        logging.info('flat image file collection info: '+ str(flat_ic.summary_info))
        flats = imageCollectionUtils.generate_flat_dict_keyedby_filter_binning(flat_ic)
        logging.info('Flat frames collected and collated.Performing average combination and bias subtraction')
        for k, v in flats.iteritems():
            logging.info('Combining images')
            master_flat = ccdproc.combine(v, method=combine_method)
            logging.info('Bias subtracting')
            bias_subtracted_master_flat = imageCollectionUtils.subtract_best_bias_temp_match(master_bias_ic,master_flat)
            # TODO: Subtract a scaled dark frame here.
            date_file_prefix  = imageCollectionUtils.extract_date_from(bias_subtracted_master_flat)
            bias_subtracted_master_flat.write('master_flat_' + date_file_prefix + k + '.fits', clobber=True)
            if bias_subtracted_master_flat.header['XBINNING'] == 1:
                logging.info('Generating scaled flat for 2xBIN from 1xBIN image')
                scaled = imageCollectionUtils.resample_to_BIN2(bias_subtracted_master_flat)
                scaled.write('master_flat_' + date_file_prefix + k +'_rescaled2X.fits', clobber=True)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    generate_flats()
