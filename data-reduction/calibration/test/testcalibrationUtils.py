import numpy as np
from unittest import TestCase
import astropy.units as u

from ccdproc import CCDData

from .. import calibrationUtils


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
        ccd = CCDData(np.zeros((10, 10)), unit=u.adu)
        ccd.header['CCD-TEMP']=-20
        ccd.header['XBINNING']=2
        ccd.header['DARKTIME']=180
        result = calibrationUtils.generate_dark_key(ccd)
        self.assertEqual('180_-20_2X',result)

    def test_generate_key_filter_binning(self):
        ccd = CCDData(np.zeros((10, 10)), unit=u.adu)
        ccd.header['CCD-TEMP']=-20
        ccd.header['XBINNING']=2
        ccd.header['DARKTIME']=180
        ccd.header['FILTER']='G'
        result = calibrationUtils.generate_key_filter_binning(ccd)
        self.assertEqual('G_2X',result)

    def test_generate_key_filter_binning_date(self):
        ccd = CCDData(np.zeros((10, 10)), unit=u.adu)
        ccd.header['FILTER']='HA'
        ccd.header['XBINNING']=2
        ccd.header['DATE-OBS']='2016-02-14T23:15:03'
        result = calibrationUtils.generate_key_filter_binning_date(ccd)
        self.assertEqual('HA_2X2016-02-14',result)

    def test_subtract_best_bias_temp_match(self):
        assert True

    def test_subtract_best_dark(self):
        assert True

    def test_flat_correct(self):
        assert True

    def test_resample_to_BIN2_from_bin2_returns_same(self):
        """
        Test error scenario cant convert from bin1
        :return:
        """
        ccd = CCDData(np.zeros((10, 10)), unit=u.adu)
        ccd.header['CCD-TEMP']=-20
        ccd.header['XBINNING']=2
        result = calibrationUtils.resample_to_BIN2(ccd)
        assert result == ccd

    def test_resample_to_BIN2(self):
        ccd = CCDData(np.arange(100).reshape(10,10), unit=u.adu)
        ccd.header['CCD-TEMP']=-20
        ccd.header['XBINNING']=1
        ccd.header['NAXIS1'] = 10
        ccd.header['NAXIS2'] = 10
        result = calibrationUtils.resample_to_BIN2(ccd)
        print result
        assert result.data[0][2] == 4
        assert result.data[2][3] == 52
        assert result.data[4][4] == 99

    def test_generate_bias_key(self):
        ccd = CCDData(np.zeros((10, 10)), unit=u.adu)
        ccd.header['CCD-TEMP']=-20
        ccd.header['XBINNING']=2
        result = calibrationUtils.generate_bias_key(ccd)
        assert result == '-20_2X'

    def test_extract_date_timestamp_from(self):
        ccd = CCDData(np.zeros((10, 10)), unit=u.adu)
        ccd.header['DATE-OBS']='2016-09-01T00:35:51'
        result = calibrationUtils.extract_date_from(ccd)
        assert result == '2016-09-01'

    def test_extract_datetime_timestamp_from(self):
        ccd = CCDData(np.zeros((10, 10)), unit=u.adu)
        ccd.header['DATE-OBS']='2016-09-01T00:35:51'
        result = calibrationUtils.extract_datetime_from(ccd)
        assert result == '2016-09-01-00-35-51'


