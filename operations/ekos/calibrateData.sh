#!/bin/bash
BASEDIR=$(dirname "$0")
echo "$BASEDIR"
dropbox start
cd ~/code/github/bh-observatory-data/data-reduction/calibration
python calibrateLightFrames.py
cd ~/code/github/bh-observatory-data/data-reduction
python addFitsObjectToFilename.py
python solveAll.py
find ~/Pictures/CalibratedLight/ -cmin -60 -exec cp {} ~/Dropbox  \;
