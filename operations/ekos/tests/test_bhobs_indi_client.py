from unittest import TestCase
from bhobs_indi_client import BhObservatoryIndiAdapter
from unittest.mock import Mock
from unittest.mock import call

class TestBhObservatoryIndiAdapter(TestCase):

    @unittest.skip("Test cannot run in travis-ci because of indi dependencies, only run local")
    def setUp(self):
        self.mock_indi_client = Mock()
        self.mock_roof_device = Mock()
        self.mock_connect_switch = StubSwitch()
        self.mock_disconnect_switch = StubSwitch()
        self.mock_switches = [self.mock_connect_switch, self.mock_disconnect_switch]
        mock_indi_client_attrs = {'getDevice.return_value': self.mock_roof_device}
        self.mock_indi_client.configure_mock(**mock_indi_client_attrs)
        mock_roof_device_attrs = {'getSwitch.return_value': self.mock_switches, 'getText.return_value' : [StubText('OPEN')]}
        self.mock_roof_device.configure_mock(**mock_roof_device_attrs)

    @unittest.skip("Test cannot run in travis-ci because of indi dependencies, only run local")
    def test_constructor(self):
        #Test
        sut = BhObservatoryIndiAdapter(self.mock_indi_client,'roof','scope','ccd')

        # Assert
        assert sut.indi_client == self.mock_indi_client
        assert sut.roof_name == 'roof'
        assert sut.telescope_name == 'scope'
        assert sut.ccd_name == 'ccd'
        self.mock_indi_client.connect.is_called()

    @unittest.skip("Test cannot run in travis-ci because of indi dependencies, only run local")
    def test_open_roof_and_roof_opens_success(self):
        #Test
        sut = BhObservatoryIndiAdapter(self.mock_indi_client,'roof','scope','ccd')
        sut.open_roof()

        # Assert
        assert self.mock_connect_switch.s == 1
        assert self.mock_disconnect_switch.s == 0
        self.mock_indi_client.sendNewSwitch.assert_called_with([self.mock_connect_switch,self.mock_disconnect_switch])
        self.mock_roof_device.getSwitch.assert_has_calls([call('CONNECTION'),call('DOME_MOTION')])
    
    @unittest.skip("Test cannot run in travis-ci because of indi dependencies, only run local")
    def test_open_roof_and_roof_fails_to_open(self):
        mock_roof_device_attrs = {'getSwitch.return_value': self.mock_switches, 'getText.return_value' : [StubText('CLOSED')]}
        self.mock_roof_device.configure_mock(**mock_roof_device_attrs)

        #Test
        sut = BhObservatoryIndiAdapter(self.mock_indi_client,'roof','scope','ccd')
        sut.retry_limit = 2
        with self.assertRaises(Exception):
            sut.open_roof()
            
    @unittest.skip("Test cannot run in travis-ci because of indi dependencies, only run local")
    def test_unpark_scope(self):
        #Test
        sut = BhObservatoryIndiAdapter(self.mock_indi_client,'roof','scope','ccd')
        sut.unpark_scope()



class StubText():
    def __init__(self, text):
        self.text = text

class StubSwitch():
    def __init__(self):
        self.s = ''
        pass
