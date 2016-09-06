from astropy import units as u

import ccdproc
from ccdproc import CCDData
import logging


def generate_bias_dict_keyedby_temp_binning(image_file_collection):
    raw_bias_frames = {}
    for filename in image_file_collection.files_filtered(FRAME='Bias'):
        ccd = CCDData.read(image_file_collection.location + filename, unit = u.adu)
        bias_key = generate_bias_key(ccd)
        if bias_key not in raw_bias_frames:
            raw_bias_frames[bias_key] = []
        raw_bias_frames[bias_key].append(ccd)
    return raw_bias_frames

def generate_flat_dict_keyedby_filter_binning(image_file_collection):
    raw_frames = {}
    for filename in image_file_collection.files_filtered(FRAME='Flat Field'):
        logging.info('processing raw flat')
        ccd = CCDData.read(image_file_collection.location + filename, unit = u.adu)
        flat_key = generate_flat_key(ccd)
        if flat_key not in raw_frames:
            raw_frames[flat_key] = []
        raw_frames[flat_key].append(ccd)
    return raw_frames

def combine_values_from_dictionary_and_write(image_dict, prefix, combination_method='average'):
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

def generate_flat_key(ccd):
    flat_key = str(ccd.header['FILTER']) + '_' \
               + str(ccd.header['XBINNING']) + 'X'
    return flat_key

# Locates The best candidate master bias and subtracts from the ccd passed. Returns the corrected ccd
# Bias frames in theory are not temperature sensitive but this will find the closest match.
def subtract_best_bias_temp_match(bias_imagefilecollection,ccd):
    temp_diff = 100
    for filename in bias_imagefilecollection.files_filtered(FRAME='Bias',XBINNING=ccd.header['XBINNING']):
        bias_candidate = CCDData.read(bias_imagefilecollection.location + filename, unit=u.adu)
        if abs(bias_candidate.header['CCD-TEMP'] - ccd.header['CCD-TEMP']) < temp_diff:
            result = bias_candidate
            temp_diff = abs(bias_candidate.header['CCD-TEMP'] - ccd.header['CCD-TEMP'])
    corrected = ccdproc.subtract_bias(ccd, result)
    logging.warn('Temperature difference between bias and image = ' + str(temp_diff))
    return corrected

