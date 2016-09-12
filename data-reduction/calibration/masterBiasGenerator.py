import json
import os
import ConfigParser
import logging
import imageCollectionUtils
import ccdproc

from ccdproc import ImageFileCollection

#
# This script is responsible for generation of a master bias images by averaging multiple bias frames.
# Calibration logic is based on AAVSO guidelines from their CCDPhotometryGuide.pdf
#
def generate_master_bias_frames():

    config = ConfigParser.ConfigParser()
    config.read('calibration.cfg')
    combine_method = config.get('Flat_Paths', 'combine_method')
    outdir = config.get('Bias_Paths', 'masterdir')
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    os.chdir(outdir)
    rawdirs_to_process = json.loads(config.get('Bias_Paths', 'rawdirs'))
    for rawdir_to_process in rawdirs_to_process:
        logging.info('processing raw dir ' + rawdir_to_process)
        ic1 = ImageFileCollection(rawdir_to_process)
        raw_bias_frames = imageCollectionUtils.generate_bias_dict_keyedby_temp_binning(ic1)
        imageCollectionUtils.combine_values_from_dictionary_and_write(raw_bias_frames, 'master_bias', combine_method)
        logging.info('Complete')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    generate_master_bias_frames()
