import sys
import os
import numpy as np

from astropy.io import fits
from astropy import units as u

import ccdproc
from ccdproc import CCDData

from ccdproc import ImageFileCollection

#
# This script is responsible for generation of master flats from a directory containing flat frames.
# Calibration logic is based on AAVSO guidelines from their CCDPhotometryGuide.pdf
#      Take 10 or more images for each filter, average (or median combine) them together, then
#      subtract the Master Dark and Master Bias to create a Master Flat.
#
def generate_flats():
    if len(sys.argv) != 4:
        print(
        'Usage:\npython masterFlatGenerator.py [full_path_to_raw_flat_data] '
        '[full_path_to_dir_containing_master_dark__and_bias] '
        '[full_path_to_reduced_data]\n')
        exit()
    indir = sys.argv[1]
    master_dir = sys.argv[2]
    outdir = sys.argv[3]

    if not os.path.isdir(outdir): os.mkdir(outdir)
    os.chdir(outdir)
    flat_ic = ImageFileCollection(indir)
    master_ic = ImageFileCollection(master_dir)

    # collect the bias frames into a dictionary keyed by binning.
    master_bias_dict = {}
    for filename in master_ic.files_filtered(FRAME='Bias'):
        bias_ccd = CCDData.read(master_ic.location + filename, unit=u.adu)
        bias_key = str(bias_ccd.header['XBINNING']) + 'X'
        print 'Bias image key - ' + bias_key
        if bias_key not in master_bias_dict:
            master_bias_dict[bias_key] = bias_ccd
    print 'Finished collecting Master Bias frames'

    # collect the raw flats and collate by filter and binning
    flats = {}
    for filename in flat_ic.files_filtered(FRAME='Flat'):
        flat_ccd = CCDData.read(flat_ic.location + filename, unit=u.adu)
        flat_key = str(int(flat_ccd.header['FILTER'])) + '_' \
                   + str(flat_ccd.header['XBINNING']) + 'X'
        print 'Flat image key - ' + flat_key
        if flat_key not in flats:
            flats[flat_key] = []
        flats[flat_key].append(flat_ccd)

    print 'Flat frames collected and collated.'
    print 'Performing average combination'
    for k, v in flats.iteritems():
        print 'Processing ' + k
        master_flat = ccdproc.combine(v, method='average')
        print 'Performing bias subtraction'
        bias_key = str(master_flat.header['XBINNING']) + 'X'
        if bias_key not in master_bias_dict:
            raise ValueError('No Master Bias was found for bias key ' + bias_key)
        bias = master_bias_dict[bias_key]
        bias_subtracted_master_flat = ccdproc.subtract_bias(master_flat, bias)
        # TODO: Subtract a scaled dark frame here.
        print 'Writing'
        bias_subtracted_master_flat.write('master_flat'+k+'.fits', clobber=True)
        print 'Complete'


if __name__ == '__main__':
    generate_flats()
