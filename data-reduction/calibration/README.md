# Calibration

Scripts for automation of basic image reduction based on ccdproc.

**Features**

1. Generation of master bias,dark and flats grouped by temperature/filter etc
2. Calibration of Light frames. Bias and dark subtraction, flat division. Automated selection of best calibration data based on filter,temperature,binning etc.
3. Archival of processed fits files.


**Dependencies**

Requires ccdproc to be installed. See http://ccdproc.readthedocs.io/en/latest/index.html

**Usage**

Update the calibration.cfg file with the paths to your raw data files and where you want to store the calibrated and master frames.

1. Generate your master bias frames by running masterBiasGenerator
2. Generate your master dark frames by running masterDarkGenerator
3. Generate your master flat frames by running masterFlatGenerator
4. Calibrate your light frames  by running masterLightGenerator