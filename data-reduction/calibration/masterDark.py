#!/usr/bin/python

import sys, getopt
import ccdproc
from astropy import units as u
import glob


def main(argv):
    input_file = ''
    output_file = ''
    master_bias_file = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:m:", ["ipath=", "ofile=", "mbias="])
    except getopt.GetoptError:
        print 'masterDark.py -i <inputpath> -o <output_file> -m <master_bias_file>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'averageCombiner.py -i <inputpath> -o <output_file>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_file = arg
        elif opt in ("-o", "--ofile"):
            output_file = arg
        elif opt in ("-m", "--mbias"):
            master_bias_file = arg
    print 'Input file is "', input_file
    print 'Output file is "', output_file
    print 'MasterBias file is "', master_bias_file
    dark_files = glob.glob(input_file)
    print dark_files
    dark_file_list = []
    for darkFile in dark_files:
        dark_ccd = ccdproc.CCDData.read(darkFile, unit=u.adu)
        bias_ccd = ccdproc.CCDData.read(master_bias_file, unit=u.adu)
        bias_subtracted_dark = ccdproc.subtract_bias(dark_ccd, bias_ccd)
        dark_file_list.append(bias_subtracted_dark)
        print 'subtracted'
    print dark_file_list
    master_dark = ccdproc.combine(dark_file_list, method='median')
    print 'done'
    master_dark.write(output_file, clobber=True)
    print 'saved'
    # ccdproc.combine(files,output_file,unit=u.adu)


if __name__ == "__main__":
    main(sys.argv[1:])
