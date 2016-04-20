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
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print 'averageCombiner.py -i <inputpath> -o <outputfile>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'averageCombiner.py -i <inputpath> -o <outputfile>'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg
   print 'Input file is "', inputfile
   print 'Output file is "', outputfile
   files = glob.glob(inputfile)
   print files
   ccdproc.combine(files,outputfile,unit=u.adu)

if __name__ == "__main__":
   main(sys.argv[1:])
