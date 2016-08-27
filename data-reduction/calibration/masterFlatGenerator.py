import sys
import os
import numpy as np

from astropy.io import fits
from astropy import units as u

import ccdproc
from ccdproc import CCDData

from ccdproc import ImageFileCollection


def generate_flats():
    if len(sys.argv) != 4:
        print(
        'Usage:\npython masterFlatGenerator.py [full_path_to_raw_light_data] [full_path_to_bias_data] [full_path_to_reduced_data]\n')
        exit()
    indir = sys.argv[1]
    bias_dir = sys.argv[2]
    outdir = sys.argv[3]

    if not os.path.isdir(outdir): os.mkdir(outdir)
    os.chdir(outdir)
    flat_ic = ImageFileCollection(indir)
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

    # collect the raw flats and collate by filter and binning subtract appropriate Bias while collecting.
    flats = {}
    for filename in flat_ic.files_filtered(FRAME='Flat'):
        light_ccd = CCDData.read(flat_ic.location + filename, unit=u.adu)
        flat_key = str(int(light_ccd.header['FILTER'])) + '_' \
                   + str(light_ccd.header['XBINNING']) + 'X'
        bias_key = str(light_ccd.header['XBINNING']) + 'X'
        print 'Flat image key - ' + flat_key
        print 'Bias image key - ' + bias_key
        if flat_key not in flats:
            flats[flat_key] = []
        print 'Performing Bias subtraction'
        if bias_key not in master_bias_dict:
            raise ValueError('No Master Bias was found for bias key (binning) ' + bias_key)
        bias = master_bias_dict[bias_key]
        bias_corrected = ccdproc.subtract_bias(light_ccd, bias)
        flats[flat_key].append(bias_corrected)

    print 'Flat frames collected and colocated.'
    print 'Performing median combination'
    for k, v in flats.iteritems():
        print 'Processing ' + k
        master_flat = ccdproc.combine(v, method='average')
        print 'Writing'
        master_flat.write('master_flat'+k+'.fits', clobber=True)
        print 'Complete'


if __name__ == '__main__':
    generate_flats()
