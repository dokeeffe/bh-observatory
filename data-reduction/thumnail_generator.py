import glob,os
from astropy.io import fits
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np
from skimage import exposure

data_files = glob.glob('/home/dokeeffe/Pictures/CalibratedLight/*/*.fits')
for data_file in data_files:
    thumb_dir = os.path.join(os.path.dirname(data_file), 'thumbnails')
    if not os.path.exists(thumb_dir):
        os.makedirs(thumb_dir)
    thumb_file = os.path.join(thumb_dir,os.path.basename(data_file).replace('.fits','.png'))
    if not os.path.exists(thumb_file):
        print('Generating thumbnail for datafile {}'.format(data_file))
        hdulist = fits.open(data_file)
        image_data = hdulist[0].data.astype(float)
        p2, p98 = np.percentile(image_data, (2, 99))
        img_rescale = exposure.rescale_intensity(image_data, in_range=(p2, p98))
        plt.imshow(img_rescale, cmap='gray')
        try:
            plt.savefig(thumb_file, bbox_inches='tight')
        except AttributeError:
            print('Failed to generate thumbnail')
        plt.clf()
        plt.close()
    else:
        print('Skipping already generated thumbnail')


