from scipy import misc
from scipy import ndimage
import glob


data_files = glob.glob('/home/dokeeffe/Desktop/xo-2b-transit-allsky/*.jpg')
for data_file in data_files:
    image_data = misc.imread(data_file)
    im_med = ndimage.median_filter(image_data, 2)
    misc.imsave(data_file, im_med)