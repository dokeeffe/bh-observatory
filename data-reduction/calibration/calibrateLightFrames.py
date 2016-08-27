import sys
import os

from astropy import units as u

import ccdproc
from ccdproc import CCDData

from ccdproc import ImageFileCollection

# This script is used to calibrate 'Light' frames containing astronomical data.
# It performs bias correction, flat division, and flat correction.
# It will auto locate the correct bias, dark and flat based on binning, temp, exposure and filter.
# Assumes all master bias,dark,and flats are already generated and located in one dir.
def calibrate_light():
    if len(sys.argv) != 4:
        print(
        'Usage:\npython calibrateLightframes.py [full_path_to_raw_light_dir] [full_path_to_master_dark_and_bias_dir] [full_path_to_reduced_data]\n')
        exit()
    indir = sys.argv[1]
    master_dir = sys.argv[2]
    outdir = sys.argv[3]

    if not os.path.isdir(outdir): os.mkdir(outdir)
    os.chdir(outdir)
    light_ic = ImageFileCollection(indir)
    master_dark_bias_ic = ImageFileCollection(master_dir)

    # collect the bias frames into a dictionary keyed by binning.
    master_bias_dict= {}
    for filename in master_dark_bias_ic.files_filtered(FRAME='Bias'):
        bias_ccd = CCDData.read(master_dark_bias_ic.location + filename, unit=u.adu)
        bias_key = str(bias_ccd.header['XBINNING']) + 'X'
        print 'Bias image key - ' + bias_key
        if bias_key not in master_bias_dict:
            master_bias_dict[bias_key] = bias_ccd
    print 'Finished collecting Master Bias frames'

# collect the dark frames into a dictionary keyed by time, binning and temp.
    master_dark_dict= {}
    for filename in master_dark_bias_ic.files_filtered(FRAME='Dark'):
        dark_ccd = CCDData.read(master_dark_bias_ic.location + filename, unit=u.adu)
        dark_key = str(int(dark_ccd.header['DARKTIME'])) + '_' \
                   + str(int(dark_ccd.header['CCD-TEMP'])) + '_' \
                   + str(dark_ccd.header['XBINNING']) + 'X'
        print 'Dark image key - ' + dark_key
        if dark_key not in master_dark_dict:
            master_dark_dict[dark_key] = dark_ccd
    print 'Finished collecting Master Dark frames'

    # collect the raw light frames and collate by time, binning and temp, subtract appropriate Bias while collecting.
    for filename in light_ic.files_filtered(FRAME='Light'):
        light_ccd = CCDData.read(light_ic.location + filename, unit=u.adu)
        dark_key = str(int(dark_ccd.header['EXPTIME'])) + '_' \
                   + str(int(dark_ccd.header['CCD-TEMP'])) + '_' \
                   + str(dark_ccd.header['XBINNING']) + 'X'
        bias_key = str(dark_ccd.header['XBINNING']) + 'X'
        print 'Dark image key - ' + dark_key
        print 'Bias image key - ' + bias_key
        print 'Performing Bias subtraction'
        if bias_key not in master_bias_dict:
            raise ValueError('No Master Bias was found for bias key (temp_binning) ' + bias_key)
        bias = master_bias_dict[bias_key]
        bias_corrected = ccdproc.subtract_bias(light_ccd, bias)
        print 'Performing Dark subtraction'
        if dark_key not in master_dark_dict:
            raise ValueError('No Master Dark was found for bias key (temp_binning) ' + dark_key)
        dark = master_dark_dict[dark_key]
        dark_corrected = ccdproc.subtract_dark(bias_corrected, dark)
        # flat_corrected = ccdproc.flat_correct(dark_corrected, flat)
        print 'Writing'
        dark_corrected.write('calibrated_'+filename+'.fits', clobber=True)
        print 'Callibrated ' + filename


if __name__ == '__main__':
    calibrate_light()
