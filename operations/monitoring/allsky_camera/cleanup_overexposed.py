from scipy import misc
import glob, os
from multiprocessing import Pool

def process_image(data_file):
    image_data = misc.imread(data_file)
    if image_data.mean() > 200:
        os.remove(data_file)
        print('Removing {} with mean of {}'.format(data_file, image_data.mean()))

if __name__ == '__main__':
    data_files = glob.glob('/home/dokeeffe/Pictures/allsky/*.jpg')
    pool = Pool()
    pool.map(process_image, data_files)
