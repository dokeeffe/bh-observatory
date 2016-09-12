import astropy
import numpy as np
import scipy
from astropy import units as u

import ccdproc
import datetime
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
        logging.info('processing raw flat ' +filename)
        ccd = CCDData.read(image_file_collection.location + filename, unit = u.adu)
        flat_key = generate_flat_key(ccd)
        if flat_key not in raw_frames:
            raw_frames[flat_key] = []
        logging.info('collating by ' + flat_key)
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
    result = None
    for filename in bias_imagefilecollection.files_filtered(FRAME='Bias',XBINNING=ccd.header['XBINNING']):
        bias_candidate = CCDData.read(bias_imagefilecollection.location + filename, unit=u.adu)
        if abs(bias_candidate.header['CCD-TEMP'] - ccd.header['CCD-TEMP']) < temp_diff:
            result = bias_candidate
            temp_diff = abs(bias_candidate.header['CCD-TEMP'] - ccd.header['CCD-TEMP'])
    if result is None:
        logging.error('Could not find bias for, binning:' + str(ccd.header['XBINNING']) + ' temp:'+str(ccd.header['CCD-TEMP']))
        #FIXME: throw an exception here, there should be no excuse for missing bias data!!!
        return ccd
    else:
        corrected = ccdproc.subtract_bias(ccd, result)
        logging.warn('Temperature difference between bias and image = ' + str(temp_diff))
        return corrected

# Locates The best candidate master dark and subtracts from the ccd passed. Returns the corrected ccd
def subtract_best_dark(dark_imagefilecollection,ccd):
    temp_diff = 100
    result = None
    for filename in dark_imagefilecollection.files_filtered(FRAME='Dark',XBINNING=ccd.header['XBINNING']):
        dark_candidate = CCDData.read(dark_imagefilecollection.location + filename, unit=u.adu)
        if abs(dark_candidate.header['CCD-TEMP'] - ccd.header['CCD-TEMP']) < temp_diff:
            result = dark_candidate
            temp_diff = abs(dark_candidate.header['CCD-TEMP'] - ccd.header['CCD-TEMP'])
    if result is None:
        logging.error('Could not find dark for, binning:' + str(ccd.header['XBINNING']) + ' temp:'+str(ccd.header['CCD-TEMP']))
        #FIXME: throw an exception here, there should be no excuse for missing data!!!
        return ccd
    else:
        corrected = ccdproc.subtract_dark(ccd, result, exposure_time='EXPTIME', exposure_unit=u.second)
        logging.warn('Temperature difference between dark and image = ' + str(temp_diff))
        return corrected

def flat_correct(flat_imagefilecollection,ccd):
    flats = generate_flat_dict_keyedby_filter_binning(flat_imagefilecollection)
    key = generate_flat_key(ccd)
    candidate_flats = flats[key]
    #TODO: find the best candidate flat based on closest in time relative to the ccd being corrected (instead of the first one in the collection)
    if candidate_flats is None:
        logging.error('Could not find flat for key ' + key)
    flat = candidate_flats[0]
    return ccdproc.flat_correct(ccd,flat)


def resample_to_BIN2(ccd):
    """
    Resample a 1x1 binned image to 2x2 using cubic interpolation. Useful for scaling flat fields.
    Do not use for dark or bias frames.
    """
    if ccd.header['XBINNING'] == 2:
        logging.error('No need to resample this image, already 2x2 binned')
        return ccd
    else:
        logging.info('Resampling image to 50% with cubic interpolation')
        image_data = np.asarray(ccd)
        scaled_data =  scipy.ndimage.zoom(image_data, .5, order=3)
        scaled_fits = CCDData(scaled_data,unit='adu')
        scaled_fits.meta = ccd.meta.copy()
        scaled_fits.header['XBINNING'] = 2
        scaled_fits.header['YBINNING'] = 2
        scaled_fits.header['NAXIS1'] = ccd.header['NAXIS1'] / 2
        scaled_fits.header['NAXIS2'] = ccd.header['NAXIS2'] / 2
        scaled_fits.header['DERIVED'] = 'resampled by bilinear interpolation from 1x1 binned image'
        return scaled_fits

def extract_timestamp_from(ccd):
    date_obs = datetime.datetime.strptime(ccd.header['DATE-OBS'], '%Y-%m-%dT%H:%M:%S')
    return "%04d-%02d-%02d" % (date_obs.year, date_obs.month, date_obs.day)