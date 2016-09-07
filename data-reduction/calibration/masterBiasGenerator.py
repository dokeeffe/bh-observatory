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
    outdir = config.get('Bias_Paths', 'masterdir')
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    os.chdir(outdir)
    ic1 = ImageFileCollection(config.get('Bias_Paths', 'rawdir'))
    logging.info('Config complete. loaded raw data image colection ' + str(ic1.summary_info))

    raw_bias_frames = imageCollectionUtils.generate_bias_dict_keyedby_temp_binning(ic1)
    imageCollectionUtils.combine_values_from_dictionary_and_write(raw_bias_frames, 'master_bias', 'average')
    logging.info('Complete')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    generate_master_bias_frames()
