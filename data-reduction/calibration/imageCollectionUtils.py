from astropy import units as u
from ccdproc import CCDData
import logging


def generate_bias_dict_keyedby_temp_binning(image_fileCollection):
    #create the bias frame
    raw_bias_frames = {}
    for filename in image_fileCollection.files_filtered(FRAME='Bias'):
        ccd = CCDData.read(image_fileCollection.location + filename, unit = u.adu)
        bias_key = generate_bias_key(ccd)
        if bias_key not in raw_bias_frames:
            raw_bias_frames[bias_key] = []
        raw_bias_frames[bias_key].append(ccd)
    return raw_bias_frames

def combine_values_from_dictionary(image_dict, prefix, combination_method='average'):
    for k, v in image_dict.iteritems():
        logging.info('Combining: Processing ' + k)
        master = ccdproc.combine(v, method=combination_method)
        master.write(prefix + k + '.fits', clobber=True)


def generate_bias_key(ccd):
    bias_key = str(int(ccd.header['CCD-TEMP'])) + '_' \
               + str(ccd.header['XBINNING']) + 'X'
    logging.info('Generated Bias Key ' + bias_key)
    return bias_key

def generate_dark_key(ccd):
    dark_key = str(int(ccd.header['DARKTIME'])) + '_' \
               + str(int(ccd.header['CCD-TEMP'])) + '_' \
               + str(ccd.header['XBINNING']) + 'X'
    return dark_key

