import sys
import os
import numpy as np
  
from astropy.io import fits
from astropy import units as u

import ccdproc 
from ccdproc import CCDData

from ccdproc import ImageFileCollection

if len(sys.argv)!=3: 
   print('Usage:\npython this_script_name.py [full_path_to_raw_data] [full_path_to_reduced_data]\n')
   exit()

indir = sys.argv[1]
outdir = sys.argv[2]

if not os.path.isdir(outdir): os.mkdir(outdir)
os.chdir(outdir)

#change this to point to your raw data directory
ic1 = ImageFileCollection(indir)

#create the bias frames
bias_list = []
for filename in ic1.files_filtered(FRAME='Bias'):
    print 'Combining'
    print  ic1.location + filename
    ccd = CCDData.read(ic1.location + filename, unit = u.adu)
    #this has to be fixed as the bias section does not include the whole section that will be trimmed
    #ccd = ccdproc.subtract_overscan(ccd, median=True,  overscan_axis=0, fits_section='[1:966,4105:4190]')
    #ccd = ccdproc.trim_image(ccd, fits_section=ccd.header['TRIMSEC'] )
    bias_list.append(ccd)
master_bias = ccdproc.combine(bias_list, method='median')
master_bias.write('master_bias.fits', clobber=True)
print 'Complete'
