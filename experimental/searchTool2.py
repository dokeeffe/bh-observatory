import fnmatch
import os
from astropy.io import fits

solved = 0
notsolved = 0
for root, dirnames, filenames in os.walk('/home/dokeeffe/Pictures/CalibratedLight'):
    for filename in fnmatch.filter(filenames, '*.fits'):
        hdulist = fits.open(os.path.join(root, filename))
        header = hdulist[0].header
        if 'CRVAL1' in header:
		solved+=1
	else:
		notsolved+=1

print solved
print notsolved
