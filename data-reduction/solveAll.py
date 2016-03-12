from astropy.io import fits
import os
import subprocess

files_in_dir = os.listdir(os.getcwd())
for file_in_dir in files_in_dir:
	if file_in_dir.endswith('fits'):
		fitsimage = fits.open(file_in_dir)
		hdr = fitsimage[0].header
		print 'Plate Solving Image: ' + file_in_dir
		focalLength = hdr.get('FOCALLEN',1995)
		binning = hdr['XBINNING']
		pixelSize = hdr['PIXSIZE1']
		arcSecPerPixel =  (pixelSize/focalLength) * 206.3 * binning
		subprocess.call(["solve-field", "--no-plots", "--no-fits2fits", "--resort", "--skip-solved", "-O", "-L", str(arcSecPerPixel*.95), "-H", str(arcSecPerPixel*1.05),"-u","app", file_in_dir] )
