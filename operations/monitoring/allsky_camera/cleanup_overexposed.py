from scipy import misc
import glob, os


data_files = glob.glob('/home/dokeeffe/Pictures/allsky/*.jpg')
for data_file in data_files:
    image_data = misc.imread(data_file)
    if image_data.mean() > 200:
        os.remove(data_file)
        print('Removing {} with mean of {}'.format(data_file, image_data.mean()))
