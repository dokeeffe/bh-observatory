from pyfirmata import Arduino, util
import pyfirmata
import time

class RoofSwitchInspector:
    """
    Handles the communication to arduino SensorReader
    The arduino firmware publishes messages using firmata once per second with sensor readings.
    This class is responsible for collection and persistance of readings.
    AttachTo: ""
    """

    NAME = "RoofSwitchInspector"

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
        :return:
        '''
        self.board.send_sysex(pyfirmata.pyfirmata.STRING_DATA, 'QUERY')

    def getstate(self):
        return self.state

    def dispose(self):
        super(RoofSwitchInspector, self).dispose()
        try:
            self.board.exit()
        except AttributeError:
            print("exit() raised an AttributeError unexpectedly!" + self.toString())

if __name__ == '__main__':
    inspector = RoofSwitchInspector('/dev/tty/ACMA001')
    print(inspector.getstate())
    inspector.query()
    time.sleep(1)
    print(inspector.getstate())


