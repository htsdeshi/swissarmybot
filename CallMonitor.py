import json
import re
import socket
import threading

#change below the auth ClueCon to the username and password for your event socket settings for FreeSwitch
class CallMonitor(object):

    def __init__(self, address, conferenceNumber, queue, irc_channel):
        self.conferenceNumber = conferenceNumber
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(address)
        self.sock.send(b'auth ClueCon\n\n')
        self.sock.send(b'events json CHANNEL_ANSWER\n\n')
        self.log = open("call.log", "wb")
        self.queue = queue
        self.irc_channel = irc_channel
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
            if event["variable_origination_callee_id_name"] == self.conferenceNumber:
                caller = event["Caller-Orig-Caller-ID-Name"]
                if re.search(r'^[0-9]{11}$', caller):
                    caller = "x-xxx-xxx-" + caller[7:]
                try:
                    self.queue.send(
                        caller + " joined the conference", self.irc_channel)
                    #print("Caller connected: ",caller)
                except:
                    # print(data)
                    pass
            self.log.write(data)
            data = data[startLocation + length:]

#change the IP to the IP of your FreeSwitch Server
#change 4224 to the extension of your main conference 
#change #pbx to the IRC channel name to announce to
def main():
    CallMonitor(("127.0.0.1", 8021), "4224", "queue", "#pbx") 
    print("Press CTRL-C to quit.")
    while True:
        pass


if __name__ == "__main__":
    main()
