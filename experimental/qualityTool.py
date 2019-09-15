import fnmatch
import os
from scipy import ndimage
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.stats import sigma_clipped_stats
from photutils import DAOStarFinder
from pylab import rcParams
from shutil import copyfile

rcParams['figure.figsize'] = 15,3

# search_ra = 18.53
# search_dec = 33.2
search_ra = 16.6
search_dec = 36.3
search_filter = 'PV'

search_radius = 1.5

for root, dirnames, filenames in os.walk('/media/dokeeffe/UUI/CalibratedLight/'):
    for filename in fnmatch.filter(filenames, '*.fits'):
        hdulist = fits.open(os.path.join(root, filename))
        header = hdulist[0].header
        ra = header['OBJCTRA']
        dec = header['OBJCTDEC']
        image_filter = header['FILTER']
        if ra > search_ra-search_radius and ra < search_ra+search_radius and dec > search_dec-search_radius and dec < search_dec+search_radius and image_filter==search_filter:
            print filename
            copyfile(os.path.join(root, filename), os.path.join('/home/dokeeffe/Desktop', filename))

            data = hdulist[0].data
            # extract sources
            # mean, median, std = sigma_clipped_stats(data, sigma=3.0, iters=5)
            # daofind = DAOStarFinder(fwhm=4.5, threshold=5. * std)
            # sources = daofind(data - median)
            sources = 10

            scaled_data = ndimage.zoom(data, .3, order=3)
            scaled_size = scaled_data.shape

            nax1 = header['NAXIS1']
            nax2 = header['NAXIS2']
            centre_y1 = int((nax2/2)-(scaled_size[1]/2))
            centre_y2 = int((nax2/2)+(scaled_size[1]/2))
            centre_x1 = int((nax1/2)-(scaled_size[0]/2))
            centre_x2 = int((nax1/2)+(scaled_size[0]/2))
            centre_data = data[centre_x1:centre_x2, centre_y1:centre_y2]

            # now generate a corner snippet the same size as the scaled image
            corner_data = data[0:scaled_size[0], 0:scaled_size[1]]
            corner_data2 = data[nax2-scaled_size[0]:nax2, nax1-scaled_size[1]:nax1]

            # generate plot
            ax = plt.subplot(141)
            plt.imshow(scaled_data, cmap='gray_r', origin='lower')
            # ax.annotate('Detected sources='+str(sources._data.size), xy=(2, 1), xytext=(3, 1.5))
            plt.subplot(142)
            plt.imshow(corner_data, cmap='gray_r', origin='lower')
            plt.subplot(143)
            plt.imshow(centre_data, cmap='gray_r', origin='lower')
            plt.subplot(144)
            plt.imshow(corner_data2, cmap='gray_r', origin='lower')



            # plt.imshow(corner_data, cmap=plt.cm.jet, alpha=0.5)
            # plt.show()
            plt.savefig(os.path.join('/home/dokeeffe/Desktop', filename+'.jpeg'))
            plt.clf()


