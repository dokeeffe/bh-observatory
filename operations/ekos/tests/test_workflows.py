from unittest import TestCase
import ConfigParser
from mock import Mock

from ..workflows import StartupWorkflow



class TestStartupWorkflow(TestCase):

    def test_start_happypath(self):
        config = ConfigParser.ConfigParser()
        config.read('ops.cfg')
        indi_client = Mock()
        roof_inspector = Mock()
        attrs = {'query.return_value': 'OPEN'}
        roof_inspector.configure_mock(**attrs)
        message_sender = Mock()
        power_controller = Mock()
        wf = StartupWorkflow(indi_client, roof_inspector, message_sender, power_controller, config)

        wf.start()

        roof_inspector.query.assert_called()
        indi_client.open_roof.assert_called_with('RollOff Simulator')
        message_sender.send_message.assert_called_with('Roof Open http://52-8.xyz/images/snapshot.jpg')
        indi_client.unpark_scope.assert_called_with('Telescope Simulator')
        indi_client.send_guide_pulse_to_mount.assert_called_with('Telescope Simulator')
        indi_client.set_ccd_temp.assert_called_with('CCD Simulator', -20)

    def test_start_when_roof_does_not_open(self):
        config = ConfigParser.ConfigParser()
        config.read('ops.cfg')
        indi_client = Mock()
        roof_inspector = Mock()
        attrs = {'query.return_value': 'CLOSED'}
        roof_inspector.configure_mock(**attrs)
        message_sender = Mock()
        power_controller = Mock()
        wf = StartupWorkflow(indi_client, roof_inspector, message_sender, power_controller, config)

        with self.assertRaises(Exception):
            wf.start()

        roof_inspector.query.assert_called()
        indi_client.open_roof.assert_called_with('RollOff Simulator')
        indi_client.unpark_scope.assert_called_with('Telescope Simulator')
        indi_client.send_guide_pulse_to_mount.assert_called_with('Telescope Simulator')
        indi_client.set_ccd_temp.assert_called_with('CCD Simulator', -20)
        message_sender.send_message.assert_called_with('ERROR: in startup procedure Roof did not open')
