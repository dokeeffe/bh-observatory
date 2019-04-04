#!/usr/bin/env python
from scipy import misc
from scipy import ndimage
import sys, os, time
import zwoasi as asi
import pickle

def capture(exposure_time, filename):
    cameras_found = asi.list_cameras()  # Models names of the connected cameras
    camera_id = 0
    camera = asi.Camera(camera_id)
    camera_info = camera.get_camera_property()
    # Use minimum USB bandwidth permitted
    camera.set_control_value(asi.ASI_BANDWIDTHOVERLOAD, camera.get_controls()['BandWidth']['MinValue'])
    time.sleep(1)
    camera.disable_dark_subtract()
    time.sleep(1)
    camera.set_control_value(asi.ASI_GAIN, 75)
    time.sleep(1)
    print('setting exposure to {} seconds'.format(float(exposure_time/1000000)))
    camera.set_control_value(asi.ASI_EXPOSURE, exposure_time)
    camera.set_control_value(asi.ASI_GAIN, 150)
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
    camera.set_image_type(asi.ASI_IMG_RAW8)
    camera.capture(filename=filename)

env_filename = os.getenv('ZWO_ASI_LIB')
filename = '/home/dokeeffe/Pictures/allsky/allsky.jpg'
asi.init(env_filename)
num_cameras = asi.get_num_cameras()
if num_cameras == 0:
    print('No cameras found')
    sys.exit(0)

exposure_index = 0
#loop until a good exposure found
valid_exposure_times = [15000000,7000000,100000]

captured = False

while not captured:
    capture(valid_exposure_times[exposure_index], filename)
    image_data = misc.imread(filename)
    print('Image average pixel = {}'.format(image_data.mean()))
    if image_data.mean() > 180:
        print('Removing overexposed image')
        os.remove(filename)
        exposure_index+=1
    else:
        print('Denoising image')
        im_med = ndimage.median_filter(image_data, 2)
        misc.imsave(filename, im_med)
        print('Saved to %s' % filename)
        captured = True
