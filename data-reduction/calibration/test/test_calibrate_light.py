from unittest import TestCase
import calibrateLightFrames


class TestCalibrate_light(TestCase):


    def test_calibrate_light(self):
        calibrateLightFrames._find_raw_dirs_to_process()
