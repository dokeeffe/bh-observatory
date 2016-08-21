import sys
from astropy.io import fits

if len(sys.argv)!=2: 
   print('Usage:\npython fitsHeaderViewerTool.py [full_path_to_file]\n')
   exit()

# Open the file header for viewing and load the header
hdulist = fits.open(sys.argv[1])
header = hdulist[0].header

# Print the header keys from the file to the terminal
print header.keys
