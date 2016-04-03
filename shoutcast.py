from threading import Thread
import time
import urllib.request
from xml.etree import ElementTree


class Shoutcast(Thread):

    def __init__(self, url, delay, queue, channels):
        Thread.__init__(self)
        self.setDaemon(1)
        self.url = url
        self.delay = delay
        self.queue = queue
        self.channels = channels

    def getSongTitle(self):
        try:
            with urllib.request.urlopen(self.url) as fp:
                doc = ElementTree.parse(fp)

            root = doc.getroot()
            songTitle = root.findall("SONGTITLE")[0].text
            return songTitle
        except:
            return ""

    def run(self):
        _songTitle = ""
        while True:
            songTitle = self.getSongTitle()
            if songTitle != _songTitle:
                for channel in self.channels:
                    self.queue.send("Now playing: " + songTitle, channel)
                _songTitle = songTitle
            time.sleep(self.delay)
