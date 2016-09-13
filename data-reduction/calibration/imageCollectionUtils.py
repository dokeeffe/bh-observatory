import datetime
import logging
import numpy as np
import scipy
from astropy import units as u
import sys

import ccdproc
from ccdproc import CCDData


def generate_bias_dict_keyedby_temp_binning(image_file_collection):
    """

    :param image_file_collection:
    :return:
    """
    raw_bias_frames = {}
    for filename in image_file_collection.files_filtered(FRAME='Bias'):
        ccd = CCDData.read(image_file_collection.location + filename, unit = u.adu)
        bias_key = generate_bias_key(ccd)
        if bias_key not in raw_bias_frames:
            raw_bias_frames[bias_key] = []
        raw_bias_frames[bias_key].append(ccd)
    return raw_bias_frames

def generate_flat_dict_keyedby_filter_binning_date(image_file_collection):
    """

    :param image_file_collection:
    :return:
    """
    raw_frames = {}
    for filename in image_file_collection.files_filtered(FRAME='Flat Field'):
        logging.debug('Collecting flat ' +filename)
        ccd = CCDData.read(image_file_collection.location + filename, unit = u.adu)
        flat_key = generate_key_filter_binning_date(ccd)
        if flat_key not in raw_frames:
            raw_frames[flat_key] = []
        logging.debug('collating flat by ' + flat_key)
        raw_frames[flat_key].append(ccd)
    return raw_frames

def generate_flat_dict_keyedby_filter_binning(image_file_collection):
    """

    :param image_file_collection:
    :return:
    """
    raw_frames = {}
    for filename in image_file_collection.files_filtered(FRAME='Flat Field'):
        logging.debug('Collecting flat ' +filename)
        ccd = CCDData.read(image_file_collection.location + filename, unit = u.adu)
        flat_key = generate_key_filter_binning(ccd)
        if flat_key not in raw_frames:
            raw_frames[flat_key] = []
        logging.debug('collating flat by ' + flat_key)
        raw_frames[flat_key].append(ccd)
    return raw_frames

def combine_values_from_dictionary_and_write(image_dict, prefix, combination_method='average'):
    """

    :param image_dict:
    :param prefix:
    :param combination_method:
    :return:
    """
    for k, v in image_dict.iteritems():
        logging.info('Combining: Processing ' + k)
        master = ccdproc.combine(v, method=combination_method)
        master.write(prefix + k + '.fits', clobber=True)


def generate_bias_key(ccd):
    """

    :param ccd:
    :return:
    """
    bias_key = str(int(ccd.header['CCD-TEMP'])) + '_' \
               + str(ccd.header['XBINNING']) + 'X'
    logging.info('Generated Bias Key ' + bias_key)
    return bias_key

def generate_dark_key(ccd):
    """

    :param ccd:
    :return:
    """
    dark_key = str(int(ccd.header['DARKTIME'])) + '_' \
               + str(int(ccd.header['CCD-TEMP'])) + '_' \
               + str(ccd.header['XBINNING']) + 'X'
    return dark_key

def generate_key_filter_binning(ccd):
    """
    :param ccd:
    :return:
    """
    key = str(ccd.header['FILTER']) + '_' \
               + str(ccd.header['XBINNING']) + 'X'
    return key

def generate_key_filter_binning_date(ccd):
    """
    :param ccd:
    :return:
    """
    date_obs = datetime.datetime.strptime(ccd.header['DATE-OBS'], '%Y-%m-%dT%H:%M:%S')
    key = str(ccd.header['FILTER']) + '_' \
          + str(ccd.header['XBINNING']) + 'X' \
          + "%04d-%02d-%02d" % (date_obs.year, date_obs.month, date_obs.day)
    return key

def subtract_best_bias_temp_match(bias_imagefilecollection,ccd):
    """
    Locates The best candidate master bias and subtracts from the ccd passed. Returns the corrected ccd
    Bias frames in theory are not temperature sensitive but this will find the closest match.
    :param bias_imagefilecollection:
    :param ccd:
    :return:
    """
    temp_diff = 100
    result = None
    for filename in bias_imagefilecollection.files_filtered(FRAME='Bias',XBINNING=ccd.header['XBINNING']):
        bias_candidate = CCDData.read(bias_imagefilecollection.location + filename, unit=u.adu)
        if abs(bias_candidate.header['CCD-TEMP'] - ccd.header['CCD-TEMP']) < temp_diff:
            result = bias_candidate
            temp_diff = abs(bias_candidate.header['CCD-TEMP'] - ccd.header['CCD-TEMP'])
    if result is None:
        logging.error('Could not find bias for, binning:' + str(ccd.header['XBINNING']) + ' temp:'+str(ccd.header['CCD-TEMP']))
        # FIXME: throw an exception here, there should be no excuse for missing bias data!!!
        return ccd
    else:
        corrected = ccdproc.subtract_bias(ccd, result)
        if temp_diff > 2:
            logging.warn('Temperature difference between bias and image = ' + str(temp_diff))
        return corrected

def subtract_best_dark(dark_imagefilecollection,ccd):
    """
    Locates The best candidate master dark and subtracts from the ccd passed. Returns the corrected ccd
    :param dark_imagefilecollection:
    :param ccd:
    :return: the corrected ccd
    """
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
        if temp_diff > 2:
            logging.warn('Temperature difference between dark and image = ' + str(temp_diff))
        return corrected

def flat_correct(flat_imagefilecollection,ccd):
    """
    Locate the appropriate flat from the imagecollection passed and correct the ccd passed
    :param flat_imagefilecollection:
    :param ccd:
    :return: the corrected image
    """
    flats = generate_flat_dict_keyedby_filter_binning(flat_imagefilecollection)
    key = generate_key_filter_binning(ccd)
    candidate_flats = flats[key]
    #TODO: find the best candidate flat based on closest in time relative to the ccd being corrected (instead of the first one in the collection)
    if candidate_flats is None:
        logging.error('Could not find flat for key ' + key)
    flat = None
    # Now locate the best flat based on date
    last_date_diff = sys.maxsize
    date_obs = datetime.datetime.strptime(ccd.header['DATE-OBS'], '%Y-%m-%dT%H:%M:%S')
    for flat_candidate in candidate_flats:
        date_flat = datetime.datetime.strptime(flat_candidate.header['DATE-OBS'], '%Y-%m-%dT%H:%M:%S')
        candidate_date_difference = abs((date_obs - date_flat).seconds)
        if candidate_date_difference < last_date_diff:
            last_date_diff = candidate_date_difference
            flat = flat_candidate
    logging.warn('Seconds time difference between flat and image = ' + str(last_date_diff))
    flat = candidate_flats[0]
    return ccdproc.flat_correct(ccd,flat)


def resample_to_BIN2(ccd):
    """
    Resample a 1x1 binned image to 2x2 using cubic interpolation and return. Useful for scaling flat field images.
    :param ccd:
    :return: the resampled image
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

def extract_date_from(ccd):
    """
    Returns a string YYYY-MM-DD from the ccd header DATE-OBS timestamp
    """
    date_obs = datetime.datetime.strptime(ccd.header['DATE-OBS'], '%Y-%m-%dT%H:%M:%S')
    return "%04d-%02d-%02d" % (date_obs.year, date_obs.month, date_obs.day)

def extract_datetime_from(ccd):
    """
    Returns a string YYYY-MM-DD-HH-MM-SS from the ccd header DATE-OBS timestamp
    """
    date_obs = datetime.datetime.strptime(ccd.header['DATE-OBS'], '%Y-%m-%dT%H:%M:%S')
    return "%04d-%02d-%02d-%02d-%02d-%02d" % (date_obs.year, date_obs.month, date_obs.day, date_obs.hour, date_obs.minute, date_obs.second)