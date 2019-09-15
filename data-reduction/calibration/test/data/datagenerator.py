import numpy as np
from ccdproc import CCDData


def setup_bias_data():
    ccd = CCDData(np.arange(10), unit="adu")
    metadata = {'XBINNING': 1, 'FRAME': 'bias', 'CCD-TEMP': -20}
    ccd.header = metadata
    ccd.write('bias-20x1.fits')

    ccd = CCDData(np.arange(10), unit="adu")
    metadata = {'XBINNING': 2, 'FRAME': 'bias', 'CCD-TEMP': -20}
    ccd.header = metadata
    ccd.write('bias-20x2.fits')

    ccd = CCDData(np.arange(10), unit="adu")
    metadata = {'XBINNING': 1, 'FRAME': 'bias', 'CCD-TEMP': -25}
    ccd.header = metadata
    ccd.write('bias-25x1.fits')

    ccd = CCDData(np.arange(10), unit="adu")
    metadata = {'XBINNING': 2, 'FRAME': 'bias', 'CCD-TEMP': -25}
    ccd.header = metadata
    ccd.write('bias-25x2.fits')

def setup_light_data():
    ccd = CCDData(np.arange(10), unit="adu")
    metadata = {'XBINNING': 1, 'FRAME': 'light', 'CCD-TEMP': -20, 'FILTER': 'Red', 'DATE-OBS': '2017-03-01T21:15:22.409' , 'EXPTIME': 120}
    ccd.header = metadata
    ccd.write('LIGHT/RED/light-20x1.fits')

    ccd = CCDData(np.arange(10), unit="adu")
    metadata = {'XBINNING': 2, 'FRAME': 'light', 'CCD-TEMP': -20, 'FILTER': 'Red', 'DATE-OBS': '2017-03-01T21:25:22.409', 'EXPTIME': 120,}
    ccd.header = metadata
    ccd.write('LIGHT/RED/light-20x2.fits')

    ccd = CCDData(np.arange(10), unit="adu")
    metadata = {'XBINNING': 1, 'FRAME': 'light', 'CCD-TEMP': -25, 'FILTER': 'Red', 'DATE-OBS': '2017-03-01T21:35:22.409', 'EXPTIME': 120}
    ccd.header = metadata
    ccd.write('LIGHT/RED/light-25x1.fits')

    ccd = CCDData(np.arange(10), unit="adu")
    metadata = {'XBINNING': 2, 'FRAME': 'light', 'CCD-TEMP': -25, 'FILTER': 'Red', 'DATE-OBS': '2017-03-01T21:45:22.409', 'EXPTIME': 120}
    ccd.header = metadata
    ccd.write('LIGHT/RED/light-25x2.fits')

    ccd = CCDData(np.arange(10), unit="adu")
    metadata = {'XBINNING': 1, 'FRAME': 'light', 'CCD-TEMP': -20, 'FILTER': 'Lum', 'DATE-OBS': '2017-03-01T21:15:22.409' , 'EXPTIME': 120}
    ccd.header = metadata
    ccd.write('LIGHT/LUM/light-20x1.fits')

    ccd = CCDData(np.arange(10), unit="adu")
    metadata = {'XBINNING': 2, 'FRAME': 'light', 'CCD-TEMP': -20, 'FILTER': 'Lum', 'DATE-OBS': '2017-03-01T21:25:22.409', 'EXPTIME': 120,}
    ccd.header = metadata
    ccd.write('LIGHT/LUM/light-20x2.fits')

    ccd = CCDData(np.arange(10), unit="adu")
    metadata = {'XBINNING': 1, 'FRAME': 'light', 'CCD-TEMP': -25, 'FILTER': 'Lum', 'DATE-OBS': '2017-03-01T21:35:22.409', 'EXPTIME': 120}
    ccd.header = metadata
    ccd.write('LIGHT/LUM/light-25x1.fits')

    ccd = CCDData(np.arange(10), unit="adu")
    metadata = {'XBINNING': 2, 'FRAME': 'light', 'CCD-TEMP': -25, 'FILTER': 'Lum', 'DATE-OBS': '2017-03-01T21:45:22.409', 'EXPTIME': 120}
    ccd.header = metadata
    ccd.write('LIGHT/LUM/light-25x2.fits')

def setup_dark_data():
    ccd = CCDData(np.arange(10), unit="adu")
    metadata = {'XBINNING': 1, 'FRAME': 'Dark', 'CCD-TEMP': -20, 'EXPTIME': 120}
    ccd.header = metadata
    ccd.write('dark-20x1_120.fits')

    ccd = CCDData(np.arange(10), unit="adu")
    metadata = {'XBINNING': 2, 'FRAME': 'Dark', 'CCD-TEMP': -20, 'EXPTIME': 120}
    ccd.header = metadata
    ccd.write('dark-20x2_120.fits')

    ccd = CCDData(np.arange(10), unit="adu")
    metadata = {'XBINNING': 1, 'FRAME': 'Dark', 'CCD-TEMP': -25, 'EXPTIME': 180}
    ccd.header = metadata
    ccd.write('dark-25x1_180.fits')

    ccd = CCDData(np.arange(10), unit="adu")
    metadata = {'XBINNING': 2, 'FRAME': 'Dark', 'CCD-TEMP': -25, 'EXPTIME': 180}
    ccd.header = metadata
    ccd.write('dark-25x2_180.fits')


def setup_flat_data():
    ccd = CCDData(np.arange(10,20), unit="adu")
    metadata = {'XBINNING': 1, 'FRAME': 'Flat Field', 'CCD-TEMP': -20, 'FILTER': 'Red', 'DATE-OBS': '2017-03-01T21:03:22.409'}
    ccd.header = metadata
    ccd.write('flat-20x1_Red-0301.fits')

    ccd = CCDData(np.arange(10,20), unit="adu")
    metadata = {'XBINNING': 2, 'FRAME': 'Flat Field', 'CCD-TEMP': -20, 'FILTER': 'Red', 'DATE-OBS': '2017-03-01T21:03:22.409'}
    ccd.header = metadata
    ccd.write('flat-20x2_Red-0301.fits')

    ccd = CCDData(np.arange(10,20), unit="adu")
    metadata = {'XBINNING': 1, 'FRAME': 'Flat Field', 'CCD-TEMP': -20, 'FILTER': 'Red', 'DATE-OBS': '2017-04-01T21:03:22.409'}
    ccd.header = metadata
    ccd.write('flat-20x1_Red-0401.fits')

    ccd = CCDData(np.arange(10,20), unit="adu")
    metadata = {'XBINNING': 2, 'FRAME': 'Flat Field', 'CCD-TEMP': -20, 'FILTER': 'Red', 'DATE-OBS': '2017-04-01T21:03:22.409'}
    ccd.header = metadata
    ccd.write('flat-20x2_Red-0401.fits')

    ccd = CCDData(np.arange(10,20), unit="adu")
    metadata = {'XBINNING': 1, 'FRAME': 'Flat Field', 'CCD-TEMP': -20, 'FILTER': 'Lum', 'DATE-OBS': '2017-03-01T21:03:22.409'}
    ccd.header = metadata
    ccd.write('flat-20x1_Lum-0301.fits')

    ccd = CCDData(np.arange(10,20), unit="adu")
    metadata = {'XBINNING': 2, 'FRAME': 'Flat Field', 'CCD-TEMP': -20, 'FILTER': 'Lum', 'DATE-OBS': '2017-03-01T21:03:22.409'}
    ccd.header = metadata
    ccd.write('flat-20x2_Lum-0301.fits')

    ccd = CCDData(np.arange(10,20), unit="adu")
    metadata = {'XBINNING': 1, 'FRAME': 'Flat Field', 'CCD-TEMP': -20, 'FILTER': 'Lum', 'DATE-OBS': '2017-04-01T21:03:22.409'}
    ccd.header = metadata
    ccd.write('flat-20x1_Lum-0401.fits')

    ccd = CCDData(np.arange(10,20), unit="adu")
    metadata = {'XBINNING': 2, 'FRAME': 'Flat Field', 'CCD-TEMP': -20, 'FILTER': 'Lum', 'DATE-OBS': '2017-04-01T21:03:22.409'}
    ccd.header = metadata
    ccd.write('flat-20x2_Lum-0401.fits')



setup_light_data()
