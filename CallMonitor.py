import json
import re
import socket
import threading
from config import (freeswitch)


class CallMonitor(object):

    def __init__(self, address, password, conference, queue, irc_channels):
        self.conferenceNumber = conference
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(address)
        authorization_string = b'auth ' + \
            password.encode('utf-8') + b'\n\n'
        self.sock.send(authorization_string)
        self.sock.send(b'events json CHANNEL_ANSWER\n\n')
        self.log = open("call.log", "wb")
        self.queue = queue
        self.irc_channels = irc_channels
        self.monitor_thread = threading.Thread(
            target=CallMonitor.run, args=(self,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    @staticmethod
    def getLength(data):
        line = data.decode('utf-8')
        match = re.search(r'Content-Length: ([0-9]*)\n', line)
        if match is not None:
            return int(match.groups()[0])
        return -1

    @staticmethod
    def getStartLocation(data):
        ct = "Content-Type: text/event-json\n\n"
        pos = data.decode('utf-8').find(ct)
        if pos > -1:
            pos += len(ct)
        return pos

    @staticmethod
    def getEvent(data):
        return json.loads(data.decode('utf-8'))

    @staticmethod
    def run(self):
        data = self.sock.recv(4096)
        while(True):
            length = self.getLength(data)
            while length == -1:
                data += self.sock.recv(4096)
                length = self.getLength(data)

            startLocation = self.getStartLocation(data)
            while startLocation == -1:
                data += self.sock.recv(4096)
                startLocation = self.getStartLocation(data)

            while len(data) - startLocation < length:
                data += self.sock.recv(4096)

            event = self.getEvent(data[startLocation:startLocation + length])
            if event["variable_origination_callee_id_name"] == freeswitch["conference"]:
                caller = event["Caller-Orig-Caller-ID-Name"]
                if re.search(r'^[0-9]{11}$', caller):
                    caller = "x-xxx-xxx-" + caller[7:]
                try:

                    self.queue.send(
                        caller + " joined the conference", freeswitch["channels"])
                    #print("Caller connected: ",caller)
                except:
                    # print(data)
                    pass
            self.log.write(data)
            data = data[startLocation + length:]
