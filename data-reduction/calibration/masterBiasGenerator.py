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
def generate_bias():

    config = ConfigParser.ConfigParser()
    config.read('calibration.cfg')
    indir = config.get('Bias_Paths', 'rawdir')
    outdir = config.get('Bias_Paths', 'masterdir')

    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    os.chdir(outdir)

    ic1 = ImageFileCollection(indir)

    #create the bias frame
    raw_bias_frames = imageCollectionUtils.generate_bias_dict_keyedby_temp_binning(ic1)
    logging.info('Combining')
    for k, v in raw_bias_frames.iteritems():
        logging.info('Processing bias collection for key ' + k)
        master_bias = ccdproc.combine(v, method='average')
        logging.info('Writing Master Bias')
        master_bias.write('master_bias'+k+'.fits', clobber=True)
        logging.info('Complete')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    generate_bias()
