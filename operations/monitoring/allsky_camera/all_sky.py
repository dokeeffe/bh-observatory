#!/usr/bin/env python
from scipy import misc
import sys, os
import zwoasi as asi

env_filename = os.getenv('ZWO_ASI_LIB')
asi.init(env_filename)
num_cameras = asi.get_num_cameras()
if num_cameras == 0:
    print('No cameras found')
    sys.exit(0)

cameras_found = asi.list_cameras()  # Models names of the connected cameras
camera_id = 0
camera = asi.Camera(camera_id)
camera_info = camera.get_camera_property()

# Use minimum USB bandwidth permitted
camera.set_control_value(asi.ASI_BANDWIDTHOVERLOAD, camera.get_controls()['BandWidth']['MinValue'])

# Set some sensible defaults. They will need adjusting depending upon
# the sensitivity, lens and lighting conditions used.
camera.disable_dark_subtract()
camera.set_control_value(asi.ASI_GAIN, 75)
camera.set_control_value(asi.ASI_EXPOSURE, 25000000)
#camera.set_control_value(asi.ASI_WB_B, 99)
#camera.set_control_value(asi.ASI_WB_R, 75)
#camera.set_control_value(asi.ASI_GAMMA, 0)
#camera.set_control_value(asi.ASI_BRIGHTNESS, 50)
#camera.set_control_value(asi.ASI_FLIP, 0)

try:
    camera.stop_exposure()
except (KeyboardInterrupt, SystemExit):
    raise
except:
    pass

print('Capturing a single 8-bit mono image')
filename = '/home/dokeeffe/Pictures/allsky/allsky.jpg'
camera.set_image_type(asi.ASI_IMG_RAW8)
camera.capture(filename=filename)
image_data = misc.imread(filename)
if image_data.mean() > 200:
    os.remove(filename)
else:
    print('Saved to %s' % filename)
