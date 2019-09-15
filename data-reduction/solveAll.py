#!/usr/bin/python

from astropy.io import fits
import os
import fnmatch
import subprocess
from shutil import copyfile
from shutil import rmtree

rmtree('/tmp/solver', ignore_errors=True)
os.mkdir('/tmp/solver')
for root, dirnames, filenames in os.walk('/home/dokeeffe/Pictures/CalibratedLight'):
    for filename in fnmatch.filter(filenames, '*.fits'):
        original_hdu = fits.open(os.path.join(root, filename))
        solved = 'CRVAL1' in original_hdu[0].header and 'CD1_1' in original_hdu[0].header
        if not solved:
            rmtree('/tmp/solver', ignore_errors=True)
            os.mkdir('/tmp/solver')
            print('solving ' + os.path.join(root, filename))
            temp_file = os.path.join('/tmp/solver', filename)
            copyfile(os.path.join(root, filename), temp_file)
            hdulist = fits.open(temp_file)
            header = hdulist[0].header
            ra = header['OBJCTRA']
            dec = header['OBJCTDEC']
            focalLength = header.get('FOCALLEN', 1800)
            print( 'focalLength ' + str(focalLength))
            binning = header['XBINNING']
            pixelSize = header['PIXSIZE1']
            arcSecPerPixel = (pixelSize / focalLength) * 206.3 * binning
            try:
                print('solve-field {} {} {} {} {} {} {} {} {} {} {} {} {} {} {}'.format('--cpulimit', '30', '--no-plots', '--resort', '--skip-solved','--downsample','2', '-O', '-L', '1.25', '-H', '1.27', '-u', 'app', temp_file))
                retcode = subprocess.call(['solve-field', '--cpulimit', '30', '--no-plots', '--resort', '--skip-solved','--downsample','2', '-O', '-L',
                         '1.25', '-H', '1.27', '-u', 'app', temp_file])
                if retcode == 0:
                    copyfile(os.path.join('/tmp/solver', filename.replace('fits', 'new')), os.path.join(root, filename))
                else:
                    print('could not solve')
            except IOError:
                print('IOerror, could not solve')
