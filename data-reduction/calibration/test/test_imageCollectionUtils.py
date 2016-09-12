from ccdproc import CCDData
import astropy.units as u
import numpy as np
from .. import imageCollectionUtils
import numpy as np
import scipy.ndimage

def test_generate_bias_key():
    ccd = CCDData(np.zeros((10, 10)), unit=u.adu)
    ccd.header['CCD-TEMP']=-20
    ccd.header['XBINNING']=2
    result = imageCollectionUtils.generate_bias_key(ccd)
    assert result == '-20_2X'

def test_extract_timestamp_from():
    ccd = CCDData(np.zeros((10, 10)), unit=u.adu)
    ccd.header['DATE-OBS']='2016-09-01T00:35:51'
    result = imageCollectionUtils.extract_timestamp_from(ccd)
    assert result == '2016'
