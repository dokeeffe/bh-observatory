from pyfirmata import Arduino, util
import pyfirmata
import time


class RollOffTimeoutException(Exception):
    pass

class RoofSwitchInspector(object):
    '''
    Responsible for connecting directly to the roof controller over USB/firmata.
    Bypassing the INDI layer and going directly to the controllers open/close limit switches seems a safer option for safety checks
    '''
    NAME = 'RoofSwitchInspector'
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'
    MESSAGE_DELAY = 1

    def __init__(self, port):
        self.state = 'UNKNOWN'
        self.board = Arduino(port)
        # start an iterator thread so that serial buffer doesn't overflow
        it = util.Iterator(self.board)
        it.start()
        self.board.add_cmd_handler(pyfirmata.pyfirmata.STRING_DATA, self._messageHandler)

    def _messageHandler(self, *args, **kwargs):
        '''
        Calback method envoked by the firmata library. Handles the string message sent from the arduino.
        :param args:
        :param kwargs:
        :return:
        '''
        self.state = util.two_byte_iter_to_str(args)

    def query(self):
        '''
        Send QUERY message to the roof device
        :return: OPEN or CLOSED or UNKNOWN
        '''
        self.board.send_sysex(pyfirmata.pyfirmata.STRING_DATA, util.str_to_two_byte_iter('QUERY'))
        time.sleep(self.MESSAGE_DELAY) #necessary to wait a short time for the message to come back over usb.
        return self.state

    def wait_until(self, required_state):
        '''
        Waits until the required state has been reached (OPEN/CLOSE)
        :param required_state:
        :return:
        '''
        retry = 0
        while retry < 30:
            if self.query() == required_state:
                return
            retry += 1
        raise RollOffTimeoutException()

    def disconnect(self):
        '''
        Disconnect firmata from the device.
        :return:
        '''
        try:
            self.board.exit()
        except AttributeError:
            print("exit() raised an AttributeError unexpectedly!" + self.toString())

if __name__ == '__main__':
    inspector = RoofSwitchInspector('/dev/ttyACM0')
    print(inspector.query())
    inspector.disconnect()


