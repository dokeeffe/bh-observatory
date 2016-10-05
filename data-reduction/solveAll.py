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
        print 'solving ' + os.path.join(root, filename)
        temp_file =  os.path.join('/tmp/solver', filename)
        copyfile(os.path.join(root, filename),temp_file)
        hdulist = fits.open(temp_file)
        header = hdulist[0].header
        ra = header['OBJCTRA']
        dec = header['OBJCTDEC']
        print 'Plate Solving Image: ' + filename
        focalLength = header.get('FOCALLEN',1800)
        binning = header['XBINNING']
        pixelSize = header['PIXSIZE1']
        arcSecPerPixel =  (pixelSize/focalLength) * 206.3 * binning
        # subprocess.call(['solve-field', '--no-plots', '--no-fits2fits', '--resort', '--skip-solved', '-O', '-L', str(arcSecPerPixel*.95), '-H', str(arcSecPerPixel*1.05),'-u','app', '/tmp/solver/tosolve.fits'] )
        params = ['solve-field', '--no-plots', '--no-fits2fits', '--resort', '--skip-solved', '-O', '-L', str(arcSecPerPixel*.95), '-H', str(arcSecPerPixel*1.05),'-u','app', temp_file]
        print params
        # copy solved file back to overwrite original
        rmtree('/tmp/solver', ignore_errors=True)
        os.mkdir('/tmp/solver')
