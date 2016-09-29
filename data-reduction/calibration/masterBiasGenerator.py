import ConfigParser
import json
import logging
import os

from ccdproc import ImageFileCollection

import calibrationUtils


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
        bias_ic = ImageFileCollection(rawdir_to_process)
        if not bias_ic.files:
            logging.warn('no data in ' + rawdir_to_process)
        else:
            logging.info('processing raw dir ' + rawdir_to_process)
            raw_bias_frames = calibrationUtils.generate_bias_dict_keyedby_temp_binning(bias_ic)
            calibrationUtils.combine_values_from_dictionary_and_write(raw_bias_frames, 'master_bias', combine_method)
            logging.info('Completed generation of master bias, archiving raw data')
            calibrationUtils.move_to_archive(rawdir_to_process, bias_ic.files_filtered(FRAME='Bias'),prefix='raw_bias_data_')
            logging.info('Completed archival of raw bias data')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    generate_master_bias_frames()
