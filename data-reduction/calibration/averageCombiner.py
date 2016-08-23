#!/usr/bin/python

#
# Combines a collection of fits files by averaging them together. 
# Used to average Bias frames to create a master bias
#

import sys, getopt
import numpy as np
import ccdproc
from astropy import units as u
import glob


def main(argv):
    input_file = ''
    output_file = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print 'averageCombiner.py -i <inputpath> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'averageCombiner.py -i <inputpath> -o <outputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_file = arg
        elif opt in ("-o", "--ofile"):
            output_file = arg
    print 'Input file is "', input_file
    print 'Output file is "', output_file
    files = glob.glob(input_file)
    print files
    ccdproc.combine(files, output_file, unit=u.adu)


if __name__ == "__main__":
    main(sys.argv[1:])
