import numpy as np
from unittest import TestCase
import astropy.units as u

from ccdproc import CCDData

from .. import imageCollectionUtils


class ImageCollectionUtilsTester(TestCase):

    def test_generate_bias_dict_keyedby_temp_binning(self):
        assert True

    def test_generate_flat_dict_keyedby_filter_binning_date(self):
        assert True

    def test_generate_flat_dict_keyedby_filter_binning(self):
        assert True

    def test_combine_values_from_dictionary_and_write(self):
        assert True

    def test_generate_dark_key(self):
        assert True

    def test_generate_key_filter_binning(self):
        assert True

    def test_generate_key_filter_binning_date(self):
        assert True

    def test_subtract_best_bias_temp_match(self):
        assert True

    def test_subtract_best_dark(self):
        assert True

    def test_flat_correct(self):
        assert True

    def test_resample_to_BIN2(self):
        assert True

    def test_generate_bias_key(self):
        ccd = CCDData(np.zeros((10, 10)), unit=u.adu)
        ccd.header['CCD-TEMP']=-20
        ccd.header['XBINNING']=2
        result = imageCollectionUtils.generate_bias_key(ccd)
        assert result == '-20_2X'

    def test_extract_date_timestamp_from(self):
        ccd = CCDData(np.zeros((10, 10)), unit=u.adu)
        ccd.header['DATE-OBS']='2016-09-01T00:35:51'
        result = imageCollectionUtils.extract_date_from(ccd)
        assert result == '2016-09-01'

    def test_extract_datetime_timestamp_from(self):
        ccd = CCDData(np.zeros((10, 10)), unit=u.adu)
        ccd.header['DATE-OBS']='2016-09-01T00:35:51'
        result = imageCollectionUtils.extract_datetime_from(ccd)
        assert result == '2016-09-01-00-35-51'


