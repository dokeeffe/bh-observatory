from unittest import TestCase
from unittest.mock import Mock
from unittest.mock import patch

from ..message_senders import SmsMessageSender


class TestSmsMessageSender(TestCase):

    @patch.object(SmsMessageSender, 'send_request')
    def test_send_message(self, mock_send_request):
        sender = SmsMessageSender('derek0207@gmail.com','abc','353876119500', test_flag=1)
        sender.urlopen = Mock()
        sender.send_message('test')
        # mock_send_request.assert_called_with('http://www.txtlocal.com/sendsmspost.php')

