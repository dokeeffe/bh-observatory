from ccdproc import CCDData
import astropy.units as u
import numpy as np
from .. import imageCollectionUtils

def test_generate_bias_key():
    ccd = CCDData(np.zeros((10, 10)), unit=u.adu)
    ccd.header['CCD-TEMP']=-20
    ccd.header['XBINNING']=2
    result = imageCollectionUtils.generate_bias_key(ccd)
    assert result == '-20_2X'

