import datetime
import logging
import numpy as np
import scipy
from astropy import units as u
import sys

import ccdproc
from ccdproc import CCDData
import zipfile
import time
import os

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
    return a dictionary keyed by filter,binning and date. The value will be an array of fits files
    :param image_file_collection:
    :return:
    """
    raw_frames = {}

    flats = image_file_collection.files_filtered(FRAME='Flat') 
    for filename in flats:
        logging.info('Collecting flat ' +filename)
        ccd = CCDData.read(image_file_collection.location + filename, unit = u.adu)
        print(ccd.header)
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
    flats = image_file_collection.files_filtered(FRAME='Flat')
    for filename in flats:
        logging.info('Collecting flat ' +filename)
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
        master = ccdproc.combine(v, method=combination_method, mem_limit=128e6)
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
    date_obs = datetime.datetime.strptime(ccd.header['DATE-OBS'], '%Y-%m-%dT%H:%M:%S.%f')
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
    best_bias = None
    best_bias_filename = ''
    for filename in bias_imagefilecollection.files_filtered(FRAME='Bias',XBINNING=ccd.header['XBINNING']):
        bias_candidate = CCDData.read(os.path.join(bias_imagefilecollection.location, filename), unit=u.adu)
        if abs(bias_candidate.header['CCD-TEMP'] - ccd.header['CCD-TEMP']) < temp_diff:
            best_bias = bias_candidate
            best_bias_filename = os.path.join(bias_imagefilecollection.location, filename)
            temp_diff = abs(bias_candidate.header['CCD-TEMP'] - ccd.header['CCD-TEMP'])
    if best_bias is None:
        raise RuntimeError('Could not find bias for, binning:' + str(ccd.header['XBINNING']) + ' temp:'+str(ccd.header['CCD-TEMP']))
        return ccd
    if best_bias.header['NAXIS1'] != ccd.header['NAXIS1'] or best_bias.header['NAXIS2'] != ccd.header['NAXIS2']:
        print(ccd.header)
        raise RuntimeError('Best match for bias does not match resolution of image {}x{}'.format(ccd.header['NAXIS1'], ccd.header['NAXIS2']))
    else:
        corrected = ccdproc.subtract_bias(ccd, best_bias)
        corrected.header['CALBIAS'] = best_bias_filename
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
    best_dark = None
    best_dark_filename = None
    for filename in dark_imagefilecollection.files_filtered(FRAME='Dark',XBINNING=ccd.header['XBINNING']):
        dark_candidate = CCDData.read(os.path.join(dark_imagefilecollection.location, filename), unit=u.adu)
        if abs(dark_candidate.header['CCD-TEMP'] - ccd.header['CCD-TEMP']) < temp_diff:
            best_dark = dark_candidate
            best_dark_filename = os.path.join(dark_imagefilecollection.location, filename)
            temp_diff = abs(dark_candidate.header['CCD-TEMP'] - ccd.header['CCD-TEMP'])
    if best_dark is None:
        logging.error('Could not find dark for, binning:' + str(ccd.header['XBINNING']) + ' temp:'+str(ccd.header['CCD-TEMP']))
        #FIXME: throw an exception here, there should be no excuse for missing data!!!
        return ccd
    else:
        corrected = ccdproc.subtract_dark(ccd, best_dark, exposure_time='EXPTIME', exposure_unit=u.second)
        corrected.header['CALDARK'] = best_dark_filename
        if temp_diff > 2:
            logging.warn('Temperature difference between dark and image = ' + str(temp_diff))
        logging.info('dark frame subtraction completed')
        return corrected

def flat_correct(flat_imagefilecollection,ccd):
    """
    Locate the appropriate flat from the imagecollection passed and correct the ccd passed
    :param flat_imagefilecollection:
    :param ccd:
    :return: the corrected image
    """
    print(flat_imagefilecollection)
    flats = generate_flat_dict_keyedby_filter_binning(flat_imagefilecollection)
    key = generate_key_filter_binning(ccd)
    if key not in flats:
        logging.error('Could not find flat for key {} in {}'.format(key, flats.keys()))
    candidate_flats = flats[key]
    flat, last_date_diff = find_closest_date_match(candidate_flats, ccd)
    logging.warn('Seconds time difference between flat and image = ' + str(last_date_diff))
    corrected = ccdproc.flat_correct(ccd,flat)
    corrected.header['CALFLATDT'] = flat.header['DATE-OBS']
    return corrected


def find_closest_date_match(candidate_ccds, ccd):
    '''
    Finds the closest match by time. Checks all candidate_ccds for the closest DATE-OBS of the passed ccd
    :param candidate_ccds:
    :param ccd:
    :return:
    '''
    result = None
    last_date_diff = sys.maxsize
    date_obs = datetime.datetime.strptime(ccd.header['DATE-OBS'], '%Y-%m-%dT%H:%M:%S.%f')
    for candidate in candidate_ccds:
        date_candidate = datetime.datetime.strptime(candidate.header['DATE-OBS'], '%Y-%m-%dT%H:%M:%S.%f')
        candidate_date_difference = abs((date_obs - date_candidate).total_seconds())
        if candidate_date_difference < last_date_diff:
            last_date_diff = candidate_date_difference
            result = candidate
    return result, last_date_diff


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
        if image_data.shape == (2529, 3354):
            logging.warn('Odd shape, going to make even before binning')
            image_data = np.delete(image_data,(0), axis=0)
        scaled_data = scipy.ndimage.zoom(image_data, .5, order=3)
        logging.info('resampled to {}'.format(scaled_data.shape)) 
        scaled_fits = CCDData(scaled_data, unit='adu')
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
    date_obs = datetime.datetime.strptime(ccd.header['DATE-OBS'], '%Y-%m-%dT%H:%M:%S.%f')
    return "%04d-%02d-%02d" % (date_obs.year, date_obs.month, date_obs.day)

def extract_datetime_from(ccd):
    """
    Returns a string YYYY-MM-DD-HH-MM-SS from the ccd header DATE-OBS timestamp
    """
    date_obs = datetime.datetime.strptime(ccd.header['DATE-OBS'], '%Y-%m-%dT%H:%M:%S.%f')
    return "%04d-%02d-%02d-%02d-%02d-%02d" % (date_obs.year, date_obs.month, date_obs.day, date_obs.hour, date_obs.minute, date_obs.second)

def move_to_archive(directory,files, prefix='uncalibrated_archive_'):
    """
    Move a collection of files into an archive. Basically write all to a zip then delete all.
    The zip file will have a prefix defaulted to uncalibrated_archive_ then a timestamp
    :param directory:
    :param files:
    :param prefix:
    :return:
    """
    try:
        import zlib
        compression = zipfile.ZIP_DEFLATED
    except:
        compression = zipfile.ZIP_STORED
    timestr = time.strftime("%Y%m%d-%H%M%S")
    zf = zipfile.ZipFile(directory + prefix + timestr + '.zip', mode='w')
    logging.info('Generating archive of raw files which have been calibrated (moving to zip file)')
    try:
        for file_to_archive in files:
            zf.write(os.path.join(directory, file_to_archive), compress_type=compression, arcname=file_to_archive)
        for file_to_archive in files:
            os.remove(os.path.join(directory, file_to_archive))
    finally:
        zf.close()
        logging.info('Processed files moved to archive ' + zf.filename);


def find_dirs_containing_fits_files(root_path):
    '''

    :param self:
    :param root_path:
    :return:
    '''
    dirs = []
    for root, subdirs, files in os.walk(root_path):
        for subdir in subdirs:
            if any(fname.endswith('.fits') for fname in os.listdir(os.path.join(root, subdir))):
                dirs.append(os.path.join(root, subdir))
    return dirs

