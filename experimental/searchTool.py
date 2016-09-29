import fnmatch
import os
from astropy.io import fits

matches = []
for root, dirnames, filenames in os.walk('/home/dokeeffe/Pictures/CalibratedLight'):
    for filename in fnmatch.filter(filenames, '*.fits'):
        matches.append(os.path.join(root, filename))
        hdulist = fits.open(os.path.join(root, filename))
        header = hdulist[0].header
        ra = header['OBJCTRA']
        dec = header['OBJCTDEC']
        if ra > 22.1 and ra < 23.4 and dec > 33.4 and dec < 34.9:
            print filename

