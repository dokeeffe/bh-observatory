import socket

COMMAND = {
    'INFO' : '{"system":{"get_sysinfo":{}}}',
    'ON' : '{"system":{"set_relay_state":{"state":1}}}',
    'OFF' : '{"system":{"set_relay_state":{"state":0}}}'
}

class SmartPlug(object):

    def __init__(self, ip):
        self.ip = ip
        self.port = 9999

    def command(self, cmd):
        sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_tcp.connect((self.ip, self.port))
        sock_tcp.send(self.encrypt(cmd))
        data = sock_tcp.recv(4096)
        sock_tcp.close()

        return self.decrypt(data[4:])

    def encrypt(self, string):
        key = 171
        result = '\0\0\0\0'
        for i in string:
            a = key ^ ord(i)
            key = a
            result += chr(a)
        return result

    def decrypt(self, string):
        key = 171
        result = ''
        for i in string:
            a = key ^ ord(i)
            key = ord(i)
            result += chr(a)
        return result

if __name__ == '__main__':
    plg = SmartPlug('192.168.2.229')
    plg.command(COMMAND['ON'])

