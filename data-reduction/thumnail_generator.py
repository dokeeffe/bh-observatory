#!/usr/bin/python3

import glob,os
from astropy.io import fits
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np
from skimage import exposure
import multiprocessing as mp

def generate_thumb(data_file):
    thumb_dir = os.path.join(os.path.dirname(data_file), '.thumbnails')
    if not os.path.exists(thumb_dir):
        print('Making .thumbnail dir {}'.format(thumb_dir))
        os.makedirs(thumb_dir)
    thumb_file = os.path.join(thumb_dir,os.path.basename(data_file).replace('.fits','.jpeg'))
    if not os.path.exists(thumb_file):
        print('    Generating thumbnail for datafile {}'.format(data_file))
        hdulist = fits.open(data_file)
        image_data = hdulist[0].data.astype(float)
        p2, p98 = np.percentile(image_data, (2, 99))
        img_rescale = exposure.rescale_intensity(image_data, in_range=(p2, p98))
        plt.imshow(img_rescale, cmap='gray')
        try:
            plt.savefig(thumb_file, bbox_inches='tight', quality=20)
        except AttributeError:
            print('Failed to generate thumbnail')
        plt.clf()
        plt.close()
    else:
        print('    Skipping already generated thumbnail')


data_files = glob.glob('/home/dokeeffe/Pictures/CalibratedLight/**/*.fits', recursive=True)
pool = mp.Pool(mp.cpu_count())
pool.map(generate_thumb, data_files)
pool.close()
