#!/usr/bin/python

import sys, getopt
import numpy as np
import ccdproc
from astropy import units as u
import glob

def main(argv):
   inputfile = ''
   outputfile = ''
   masterbiasfile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:m:",["ipath=","ofile=","mbias="])
   except getopt.GetoptError:
      print 'masterDark.py -i <inputpath> -o <outputfile> -m <masterbiasfile>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'averageCombiner.py -i <inputpath> -o <outputfile>'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg
      elif opt in ("-m", "--mbias"):
         masterbiasfile = arg
   print 'Input file is "', inputfile
   print 'Output file is "', outputfile
   print 'MasterBias file is "', masterbiasfile
   files = glob.glob(inputfile)
   print files
#   ccdproc.combine(files,outputfile,unit=u.adu)

if __name__ == "__main__":
   main(sys.argv[1:])
