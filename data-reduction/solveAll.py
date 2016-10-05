from astropy.io import fits
import os
import fnmatch
import subprocess
from shutil import copyfile


for root, dirnames, filenames in os.walk('/home/dokeeffe/Pictures/CalibratedLight'):
    for filename in fnmatch.filter(filenames, '*.fits'):
        print 'solving'
        copyfile(filename, '/tmp/solver/tosolve.fits')
        # hdulist = fits.open(os.path.join(root, filename))
		# header = hdulist[0].header
		# ra = header['OBJCTRA']
		# dec = header['OBJCTDEC']
		# print 'Plate Solving Image: ' + filename
		# focalLength = header.get('FOCALLEN',1800)
		# binning = header['XBINNING']
		# pixelSize = header['PIXSIZE1']
		# arcSecPerPixel =  (pixelSize/focalLength) * 206.3 * binning
		# subprocess.call(['solve-field', '--no-plots', '--no-fits2fits', '--resort', '--skip-solved', '-O', '-L', str(arcSecPerPixel*.95), '-H', str(arcSecPerPixel*1.05),'-u','app', '/tmp/solver/tosolve.fits'] )
