import sys
import os
import numpy as np

from astropy.io import fits
from astropy import units as u

import ccdproc
from ccdproc import CCDData

from ccdproc import ImageFileCollection


def generate_darks():
    if len(sys.argv) != 4:
        print(
        'Usage:\npython masterDarkGenerator.py [full_path_to_raw_dark_data] [full_path_to_bias_data] [full_path_to_reduced_data]\n')
        exit()
    indir = sys.argv[1]
    bias_dir = sys.argv[2]
    outdir = sys.argv[3]

    if not os.path.isdir(outdir): os.mkdir(outdir)
    os.chdir(outdir)
    dark_ic = ImageFileCollection(indir)
    bias_ic = ImageFileCollection(bias_dir)

    # collect the bias frames into a dictionary keyed by binning.
    master_bias_dict= {}
    for filename in bias_ic.files_filtered(FRAME='Bias'):
        bias_ccd = CCDData.read(bias_ic.location + filename, unit=u.adu)
        bias_key = str(bias_ccd.header['XBINNING']) + 'X'
        print 'Bias image key - ' + bias_key
        if bias_key not in master_bias_dict:
            master_bias_dict[bias_key] = bias_ccd
    print 'Finished collecting Master Bias frames'

    # collect the raw darks and collate by binning and temp, subtract appropriate Bias while collecting.
    darks = {}
    for filename in dark_ic.files_filtered(FRAME='Dark'):
        dark_ccd = CCDData.read(dark_ic.location + filename, unit=u.adu)
        dark_key = str(int(dark_ccd.header['DARKTIME'])) + '_' \
                   + str(int(dark_ccd.header['CCD-TEMP'])) + '_' \
                   + str(dark_ccd.header['XBINNING']) + 'X'
        bias_key = str(dark_ccd.header['XBINNING']) + 'X'
        print 'Dark image key - ' + dark_key
        print 'Bias image key - ' + bias_key
        if dark_key not in darks:
            darks[dark_key] = []
        print 'Performing Bias subtraction'
        if bias_key not in master_bias_dict:
            raise ValueError('No Master Bias was found for bias key (temp_binning) ' + bias_key)
        bias = master_bias_dict[bias_key]
        bias_corrected = ccdproc.subtract_bias(dark_ccd, bias)
        darks[dark_key].append(bias_corrected)

    print 'Dark frames collected and colocated by time,temperature and binning.'
    print 'Performing median combination subtraction'
    for k, v in darks.iteritems():
        print 'Processing ' + k
        master_dark = ccdproc.combine(v, method='average')
        print 'Writing'
        master_dark.write('master_dark'+k+'.fits', clobber=True)
        print 'Complete'


if __name__ == '__main__':
    generate_darks()
