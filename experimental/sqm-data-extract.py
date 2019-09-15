import fnmatch
import os
from astropy.io import fits

# for root, dirnames, filenames in os.walk('/home/dokeeffe/Pictures/CalibratedLight'):
for root, dirnames, filenames in os.walk('/home/dokeeffe/Pictures/CalibratedLight'):
    for filename in fnmatch.filter(filenames, '*.fits'):
        hdulist = fits.open(os.path.join(root, filename))
        header = hdulist[0].header
        if 'MPSAS' in header:
            sqm = header['MPSAS']
            date_obs = header['DATE-OBS']
            print('{};{};;;;{}'.format(date_obs,date_obs,sqm))
