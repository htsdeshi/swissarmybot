import json
import re
import socket
import threading


class CallMonitor(object):

    def __init__(self, address, password, conference, queue, irc_channels):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(address, password)

        self.conferenceNumber = conference
        self.queue = queue
        self.irc_channels = irc_channels

        self.log = open("call.log", "wb")
        self.monitor_thread = threading.Thread(
            target=CallMonitor.run, args=(self,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def connect(self, address, password):
        self.sock.connect(address)
        authorization_string = 'auth ' + password + '\n\n'
        self.sock.send(authorization_string.encode('utf-8'))
        self.sock.send(b'events json CHANNEL_ANSWER\n\n')

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
            if event["variable_origination_callee_id_name"] == self.conferenceNumber:
                caller = event["Caller-Orig-Caller-ID-Name"]
                if re.search(r'^[0-9]{11}$', caller):
                    caller = "(" + caller[1:4] + ") xxx-xxxx"
                for channel in self.irc_channels:
                    try:
                        self.queue.send(
                            caller + " joined the conference", channel)
                    except:
                        print("Exception while sending to the queue")
            self.log.write(data)
            data = data[startLocation + length:]


class CallHangMonitor(object):

    def __init__(self, address, password, conference, queue, irc_channels):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(address, password)

        self.conferenceNumber = conference
        self.queue = queue
        self.irc_channels = irc_channels

        self.log = open("call.log", "wb")
        self.monitor_thread = threading.Thread(
            target=CallHangMonitor.run, args=(self,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def connect(self, address, password):
        self.sock.connect(address)
        authorization_string = 'auth ' + password + '\n\n'
        self.sock.send(authorization_string.encode('utf-8'))
        self.sock.send(b'events json CHANNEL_HANGUP\n\n')

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
            if event["variable_origination_callee_id_name"] == self.conferenceNumber:
                caller = event["Caller-Orig-Caller-ID-Name"]
                if re.search(r'^[0-9]{11}$', caller):
                    caller = "(" + caller[1:4] + ") xxx-xxxx"
                for channel in self.irc_channels:
                    try:
                        self.queue.send(
                            caller + " left the conference", channel)
                    except:
                        print("Exception while sending to the queue")
            self.log.write(data)
            data = data[startLocation + length:]
