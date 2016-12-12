from unittest import TestCase
import configparser
from unittest.mock import Mock

from workflows import StartupWorkflow, ShutdownWorkflow

class TestStartupWorkflow(TestCase):

    def test_start_roof_opens(self):
        config = configparser.ConfigParser()
        config.read('ops.cfg')
        indi_client = Mock()
        message_sender = Mock()
        power_controller = Mock()
        wf = StartupWorkflow(indi_client, message_sender, power_controller, config)

        # Test
        wf.start()

        # Assert
        indi_client.open_roof.assert_called_with()
        message_sender.send_message.assert_called_with('Roof Open http://52-8.xyz/images/snapshot.jpg')
        indi_client.unpark_scope.assert_called_with()
        indi_client.send_guide_pulse_to_mount.assert_called_with()
        indi_client.set_ccd_temp.assert_called_with(-20)

    def test_start_when_roof_does_not_open_then_exception_raised_and_message_sent(self):
        config = configparser.ConfigParser()
        config.read('ops.cfg')
        indi_client = Mock()
        indi_client_attrs = {'open_roof.side_effect': RuntimeError('Roof did not open')}
        indi_client.configure_mock(**indi_client_attrs)
        message_sender = Mock()
        power_controller = Mock()
        wf = StartupWorkflow(indi_client, message_sender, power_controller, config)

        # Test
        with self.assertRaises(Exception):
            wf.start()

        # Assert
        indi_client.open_roof.assert_called_with()
        indi_client.unpark_scope.assert_not_called()
        indi_client.send_guide_pulse_to_mount.assert_not_called()
        message_sender.send_message.assert_called_with('ERROR: in startup procedure Roof did not open')

class TestShutdownWorkflow(TestCase):

    def test_start_telescope_parked_then_roof_closes_ok(self):
        config = configparser.ConfigParser()
        config.read('ops.cfg')
        indi_client = Mock()
        indi_client_attrs = {'get_ccd_temp.return_value': 5}
        indi_client.configure_mock(**indi_client_attrs)
        message_sender = Mock()
        power_controller = Mock()
        wf = ShutdownWorkflow(indi_client, message_sender, power_controller, config)

        # Test
        wf.start()

        # Assert
        indi_client.close_roof.assert_called_with()
        indi_client.set_ccd_temp.assert_called_with(-0.0)
        message_sender.send_message.assert_called_with('Roof Closed http://52-8.xyz/images/snapshot.jpg')
        power_controller.poweroff_equipment.assert_any_call()
        power_controller.poweroff_pc.assert_any_call()

    def test_start_telescope_parked_and_roof_does_not_close_then_exception_raised_and_message_sent(self):
        config = configparser.ConfigParser()
        config.read('ops.cfg')
        indi_client = Mock()
        indi_client_attrs = {'get_ccd_temp.return_value': 5, 'close_roof.side_effect': RuntimeError('Roof did not close')}
        indi_client.configure_mock(**indi_client_attrs)
        message_sender = Mock()
        power_controller = Mock()
        wf = ShutdownWorkflow(indi_client, message_sender, power_controller, config)

        # Test
        with self.assertRaises(Exception):
            wf.start()

        # Assert
        indi_client.close_roof.assert_called_with()
        indi_client.set_ccd_temp.assert_called_with(-0.0)
        message_sender.send_message.assert_called_with('ERROR: closing roof: Roof did not close')
        power_controller.poweroff_equipment.assert_any_call()
        power_controller.poweroff_pc.assert_not_called()

    def test_start_telescope_not_parked_then_roof_does_not_close_exception_raised_and_message_sent(self):
        config = configparser.ConfigParser()
        config.read('ops.cfg')
        indi_client = Mock()
        indi_client_attrs = {'telescope_parked.return_value': False, 'get_ccd_temp.return_value': 5}
        indi_client.configure_mock(**indi_client_attrs)
        message_sender = Mock()
        power_controller = Mock()
        wf = ShutdownWorkflow(indi_client, message_sender, power_controller, config)

        # Test
        with self.assertRaises(Exception):
            wf.start()

        # Assert
        indi_client.close_roof.assert_not_called()
        indi_client.set_ccd_temp.assert_called_with(-0.0)
        message_sender.send_message.assert_called_with('ERROR: closing roof: Cannot close roof as the telescope is not parked')
        power_controller.poweroff_equipment.assert_any_call()
        power_controller.poweroff_pc.assert_not_called()