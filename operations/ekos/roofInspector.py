from pyfirmata import Arduino, util
import pyfirmata
import time

class RoofSwitchInspector:

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
        self.board.send_sysex(pyfirmata.pyfirmata.STRING_DATA, util.str_to_two_byte_iter('QUERY'))

    def getstate(self):
        self.query()
        time.sleep(0.5) 
        return self.state

    def disconnect(self):
        try:
            self.board.exit()
        except AttributeError:
            print("exit() raised an AttributeError unexpectedly!" + self.toString())

if __name__ == '__main__':
    inspector = RoofSwitchInspector('/dev/ttyACM0')
    print(inspector.getstate())
    inspector.disconnect()


