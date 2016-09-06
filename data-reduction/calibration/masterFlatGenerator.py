import ConfigParser
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
    flat_ic = ImageFileCollection(config.get('Flat_Paths', 'rawdir'))
    master_bias_ic = ImageFileCollection(config.get('Bias_Paths', 'masterdir'))
    # master_dark_ic = ImageFileCollection(config.get('Dark_Paths', 'masterdir'))
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    os.chdir(outdir)

    # collect the raw flats in a dictionary and collate by filter and binning
    logging.info('flat image file collection info: '+ str(flat_ic.summary_info))
    flats = imageCollectionUtils.generate_flat_dict_keyedby_filter_binning(flat_ic)

    logging.info('Flat frames collected and collated.Performing average combination and bias subtraction')
    for k, v in flats.iteritems():
        logging.info('Combining images')
        master_flat = ccdproc.combine(v, method='median')
        logging.info('Bias subtracting')
        bias_subtracted_master_flat = imageCollectionUtils.subtract_best_bias_temp_match(master_bias_ic,master_flat)
        # TODO: Subtract a scaled dark frame here.
        bias_subtracted_master_flat.write('master_flat_'+k+'.fits', clobber=True)
        logging.info('Completed writing master_flat_'+k+'.fits' )


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    generate_flats()
