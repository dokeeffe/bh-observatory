import numpy as np
import os
from unittest import TestCase
import astropy.units as u

from ccdproc import CCDData
from ccdproc import ImageFileCollection

import calibrationUtils


class ImageCollectionUtilsTester(TestCase):

    def test_generate_bias_dict_keyedby_temp_binning(self):
        assert True

    def test_generate_flat_dict_keyedby_filter_binning_date(self):
        assert True

    def test_generate_flat_dict_keyedby_filter_binning(self):
        assert True

    def test_combine_values_from_dictionary_and_write(self):
        assert True
        # TODO: test this!

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
        # arrange
        ccd = CCDData(np.zeros((10, 10)), unit=u.adu)
        ccd.header['FILTER']='HA'
        ccd.header['XBINNING']=2
        ccd.header['DATE-OBS']='2016-02-14T23:15:03.3'

        # act
        result = calibrationUtils.generate_key_filter_binning_date(ccd)

        # assert
        self.assertEqual('HA_2X2016-02-14',result)

    def test_subtract_best_bias_temp_match(self):
        # arrange
        ccd = CCDData(np.arange(10, 20), unit="adu")
        metadata = {'XBINNING': 1, 'FRAME': 'light', 'CCD-TEMP': -20}
        ccd.header = metadata
        bias_imagefilecollection = ImageFileCollection('data/')

        # act
        result = calibrationUtils.subtract_best_bias_temp_match(bias_imagefilecollection,ccd)

        # assert
        self.assertListEqual([10, 10, 10, 10, 10, 10, 10, 10, 10, 10],list(result.data))
        self.assertEqual('data/bias-20x1.fits',result.header['CALBIAS'])

    def test_subtract_best_dark(self):
        # arrange
        ccd = CCDData(np.arange(10,20), unit="adu")
        metadata = {'XBINNING': 2, 'FRAME': 'light', 'CCD-TEMP': -20, 'EXPTIME': 120}
        ccd.header = metadata
        dark_imagefilecollection = ImageFileCollection('data/')

        # act
        result = calibrationUtils.subtract_best_dark(dark_imagefilecollection,ccd)

        # assert
        self.assertListEqual([10, 10, 10, 10, 10, 10, 10, 10, 10, 10],list(result.data))
        self.assertEqual('data/dark-20x2_120.fits', result.header['CALDARK'])

    def test_flat_correct(self):
        # arrange
        ccd = CCDData(np.arange(100,110), unit="adu")
        metadata = {'XBINNING': 2, 'FRAME': 'light', 'CCD-TEMP': -20, 'EXPTIME': 120, 'FILTER': 'Lum', 'DATE-OBS': '2017-04-01T19:03:22.111'}
        ccd.header = metadata
        flat_imagefilecollection = ImageFileCollection('data/')

        # act
        result = calibrationUtils.flat_correct(flat_imagefilecollection,ccd)

        # assert
        self.assertEqual(145, result.data[0])
        self.assertEqual('2017-04-01T21:03:22.409', result.header['CALFLATDT'])

    def test_resample_to_BIN2_from_bin2_returns_same(self):
        """
        Test error scenario cant convert from bin1
        :return:
        """
        ccd = CCDData(np.zeros((10, 10)), unit=u.adu)
        ccd.header['CCD-TEMP']=-20
        ccd.header['XBINNING']=2
        result = calibrationUtils.resample_to_BIN2(ccd)
        self.assertEquals(result, ccd)

    def test_resample_to_BIN2(self):
        ccd = CCDData(np.arange(100).reshape(10,10), unit=u.adu)
        ccd.header['CCD-TEMP']=-20
        ccd.header['XBINNING']=1
        ccd.header['NAXIS1'] = 10
        ccd.header['NAXIS2'] = 10
        result = calibrationUtils.resample_to_BIN2(ccd)
        print(result)
        self.assertEquals(result.data[0][2], 4)
        self.assertEquals(result.data[2][3], 52)
        self.assertEquals(result.data[4][4], 99)

    def test_generate_bias_key(self):
        ccd = CCDData(np.zeros((10, 10)), unit=u.adu)
        ccd.header['CCD-TEMP']=-20
        ccd.header['XBINNING']=2
        result = calibrationUtils.generate_bias_key(ccd)
        self.assertEquals('-20_2X', result)

    def test_extract_date_timestamp_from(self):
        ccd = CCDData(np.zeros((10, 10)), unit=u.adu)
        ccd.header['DATE-OBS']='2016-09-01T00:35:51.3'
        result = calibrationUtils.extract_date_from(ccd)
        self.assertEquals('2016-09-01', result)

    def test_extract_datetime_timestamp_from(self):
        ccd = CCDData(np.zeros((10, 10)), unit=u.adu)
        ccd.header['DATE-OBS']='2016-09-01T00:35:51.3'

        result = calibrationUtils.extract_datetime_from(ccd)
        self.assertEquals('2016-09-01-00-35-51', result)

    def test_find_dirs_containing_fits_files(self):
        # arrange
        directory = os.path.join(os.getcwd(), 'data')

        # act
        result = calibrationUtils.find_dirs_containing_fits_files(directory)

        # assert
        self.assertEquals(os.path.join(os.getcwd(), 'data/LIGHT/RED'), result[0])
        self.assertEquals(os.path.join(os.getcwd(), 'data/LIGHT/LUM'), result[1])
        self.assertEquals(2, len(result))



