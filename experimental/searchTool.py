import fnmatch
import os
from astropy.io import fits

search_ra = 18.53
search_dec = 33.2
search_radius = 1.5

for root, dirnames, filenames in os.walk('/home/dokeeffe/Pictures/CalibratedLight'):
    for filename in fnmatch.filter(filenames, '*.fits'):
        hdulist = fits.open(os.path.join(root, filename))
        header = hdulist[0].header
        ra = header['OBJCTRA']
        dec = header['OBJCTDEC']
        if ra > search_ra-search_radius and ra < search_ra+search_radius and dec > search_dec-search_radius and dec < search_dec+search_radius:
            print filename

