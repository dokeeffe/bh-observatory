import sys
import os
import numpy as np
  
from astropy.io import fits
from astropy import units as u

import ccdproc 
from ccdproc import CCDData

from ccdproc import ImageFileCollection

def generate_bias():
    if len(sys.argv)!=3:
       print('Usage:\npython this_script_name.py [full_path_to_raw_data] [full_path_to_reduced_data]\n')
       exit()

    indir = sys.argv[1]
    outdir = sys.argv[2]

    if not os.path.isdir(outdir): os.mkdir(outdir)
    os.chdir(outdir)

    ic1 = ImageFileCollection(indir)

    #create the bias frames
    bias_list = []
    for filename in ic1.files_filtered(FRAME='Bias'):
        print 'Selecting image - '
        print  ic1.location + filename
        ccd = CCDData.read(ic1.location + filename, unit = u.adu)
        bias_key = str(int(ccd.header['CCD-TEMP'])) + '_' \
                   + str(ccd.header['XBINNING']) + 'X'
        print bias_key
        bias_list.append(ccd)
    print 'Combining'
    master_bias = ccdproc.combine(bias_list, method='average')
    print 'Writing'
    master_bias.write('master_bias.fits', clobber=True)
    print 'Complete'

if __name__ == '__main__':
    generate_bias()
