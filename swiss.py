#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import irc.client
import socket
import calendar
import subprocess
import optparse
import smtplib


from email.mime.text import MIMEText
from irc.client import SimpleIRCClient
from threading import (Thread, Event)
from datetime import (timedelta)
from django.utils.encoding import smart_bytes
from urllib.request import (URLError, HTTPError)
from config import (
    swiss, network, shoutcast)
from shoutcast import Shoutcast

# gather song request info including nickname who used trigger, artist,
# and song title, and send via email.


class Queue_Manager(Thread):

    def __init__(self, connection):
        Thread.__init__(self)
        self.setDaemon(1)
        self.connection = connection
        self.event = Event()
        self.queue = []

    def run(self):
        while 1:
            self.event.wait()
            while self.queue:
                (msg, target) = self.queue.pop(0)
                self.connection.privmsg(target, msg)
            self.event.clear()

    def send(self, msg, target):
        self.queue.append((msg.strip(), target))
        self.event.set()


class _swiss(SimpleIRCClient):

    def __init__(self):
        irc.client.SimpleIRCClient.__init__(self)
        self.start_time = time.time()
        self.queue = Queue_Manager(self.connection)
        self.shoutcast = Shoutcast(
            shoutcast["server"], shoutcast["pull_delay"], self.queue, shoutcast["channels"])

        self.BLACK = '\x0301'
        self.BLUE = '\x0302'
        self.RED = '\x0304'
        self.YELLOW = '\x0308'
        self.GREEN = '\x0303'
        self.PURPLE = '\x0306'
        self.PINK = '\x0313'
        self.ORANGE = '\x0307'
        self.TEAL = '\x0310'
        self.BOLD = '\x02'
        self.ITALIC = '\x1D'
        self.UNDERLINE = '\x1F'
        self.SWAP = '\x16'
        self.END = '\x0F'

    def on_welcome(self, serv, ev):
        if network['password']:
            serv.privmsg(
                "nickserv", "IDENTIFY {}".format(network['password']))
            serv.privmsg("chanserv", "SET irc_auto_rejoin ON")
            serv.privmsg("chanserv", "SET irc_join_delay 0")
        for channel in network['channels']:
            serv.join(channel)
        try:
            self.history_manager()
            time.sleep(5)
            self.queue.start()
            self.shoutcast.start()
        except (OSError, IOError) as error:
            serv.disconnect()
            print(error)
            sys.exit(1)

    def on_kick(self, serv, ev):
        serv.join(ev.target)

    def on_invite(self, serv, ev):
        serv.join(ev.argument[0])

    def on_ctcp(self, serv, ev):
        if ev.arguments[0].upper() == 'VERSION':
            serv.ctcp_reply(
                ev.source.split('!')[0], network['bot_name'])

    def history_manager(self):
        home = '{}/.swiss_logs'.format(os.environ.get('HOME'))
        self.swiss_path = os.path.dirname(os.path.realpath(__file__))
        self.announce_entries = '{}/announce-entries'.format(home)
        self.request_entries = '{}/request-entries'.format(home)
        self.irc_entries = '{}/irc-entries'.format(home)
        if os.path.exists(home) is False:
            os.system('mkdir {}'.format(home))
        if os.path.exists(self.announce_entries) is False:
            os.system('touch {}'.format(self.announce_entries))
        if os.path.exists(self.request_entries) is False:
            os.system('touch {}'.format(self.request_entries))
        if os.path.exists(self.irc_entries) is False:
            os.system('touch {}'.format(self.irc_entries))

    def restart_bot(self, serv, ev):
        serv.disconnect()
        if swiss['mode'] == 'screen':
            current_screen = self.get_current_screen()
            os.system('{0} {1}/./swiss.py run && screen -X -S {2} kill'
                      .format(swiss['start_bot'], self.swiss_path,
                              current_screen))
        else:
            os.system('{}/./swiss.py start'.format(self.swiss_path))
        sys.exit(1)

    def get_current_screen(self):
        screen_list = subprocess.getoutput('screen -list')
        screen_lines = smart_bytes(
            screen_list.replace('\t', '')).splitlines()
        for screen in screen_lines:
            if 'swiss' in screen:
                current_screen = screen.split('.')[0]
        return current_screen

    def timestamp(self, date):
        return calendar.timegm(date.timetuple())

    def get_nice_size(self, num, suffix='B'):
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

    def get_rls_pretime(self, pre):
        (years, remainder) = divmod(pre, 31556926)
        (days, remainder1) = divmod(remainder, 86400)
        (hours, remainder2) = divmod(remainder1, 3600)
        (minutes, seconds) = divmod(remainder2, 60)
        if pre < 60:
            pretime = '{}secs after Pre'.format(seconds)
        elif pre < 3600:
            pretime = '{0}min {1}secs after Pre'.format(minutes, seconds)
        elif pre < 86400:
            pretime = '{0}h {1}min after Pre'.format(hours, minutes)
        elif pre < 172800:
            pretime = '{0}jour {1}h after Pre'.format(days, hours)
        elif pre < 31556926:
            pretime = '{0}jours {1}h after Pre'.format(days, hours)
        elif pre < 63113852:
            pretime = '{0}an {1}jours after Pre'.format(years, days)
        else:
            pretime = '{0}ans {1}jours after Pre'.format(years, days)
        return pretime

    def on_privmsg(self, serv, ev):
        author = ev.source
        message = ev.arguments[0].strip()
        arguments = message.split(' ')
        if author in swiss['bot_owner']:
            if '.say' == arguments[0] and len(arguments) > 2:
                serv.privmsg(
                    arguments[1], message.replace(arguments[0], '')
                                         .replace(arguments[1], '')[2:])
            if '.act' == arguments[0] and len(arguments) > 2:
                serv.action(
                    arguments[1], message.replace(arguments[0], '')
                                         .replace(arguments[1], '')[2:])
            if '.join' == arguments[0] and len(arguments) > 2:
                serv.join(message[3:])
            if '.part' == arguments[0] and len(arguments) > 2:
                serv.part(message[3:])

    def on_pubmsg(self, serv, ev):
        author = ev.source
        message = ev.arguments[0].strip()
        arguments = message.split(' ')
        event_time = time.strftime('[%H:%M:%S]', time.localtime())
        record = '{0} {1}: {2}'.format(event_time, author, message)
        FILE = open(self.irc_entries, "a")
        FILE.write("{}\n".format(record))
        FILE.close()
        print(record)
        chan = ev.target
        if author in swiss['bot_owner']:
            try:
                if ev.arguments[0].lower() == '.restart':
                    self.restart_bot(serv, ev)
                if ev.arguments[0].lower() == '.quit':
                    serv.disconnect()
                    if not swiss['mode']:
                        os.system(swiss['kill_bot'])
                    sys.exit(1)
            except OSError as error:
                serv.disconnect()
                print(error)
                sys.exit(1)

    
        if '.song' == arguments[0].lower():
            serv.privmsg(
                chan, self.shoutcast.getSongTitle())

        if '.url' == arguments[0].lower():
            serv.privmsg(
                chan, '{0}{2}ShoutCast URL: {1}{0}{3}'.format(
                    self.BOLD, self.END, self.BLUE, shoutcast['shoutcast_feed']))

       
        if '.help' == arguments[0].lower():
            serv.privmsg(
                chan, '{0}{2}{3}Available commands:{1}{0} .help || '
                      '.version || .uptime || '
                      '.info || .url || .conf || .request artist song || .song{1}'.format(
                          self.BOLD, self.END, self.UNDERLINE, self.BLUE))

        if '.version' == arguments[0].lower():
            serv.privmsg(chan, '{0}{1}{2}{3}'.format(
                self.BOLD, self.PINK, network['bot_name'], self.END))

        if '.request' == arguments[0].lower():
            serv.privmsg(
                chan, '{0}{2}{3}Song has been requested'.format(
                    self.BOLD, self.END, self.UNDERLINE, self.BLUE))

        if '.uptime' == arguments[0].lower():
            uptime_raw = round(time.time() - self.start_time)
            uptime = timedelta(seconds=uptime_raw)
            serv.privmsg(chan, '{0}{3}[UPTIME]{4} {2}{1}'.format(
                self.BOLD, self.END, uptime, self.TEAL, self.BLACK))

        if '.get' == arguments[0].lower() and len(arguments) > 1:
            try:
                self.search_release(serv, ev, message, chan)
            except (HTTPError, URLError, KeyError,
                    ValueError, TypeError, AttributeError):
                serv.privmsg(
                    chan, '{0}Nothing found, sorry about this.{1}'.format(
                        self.BOLD, self.END))
                pass
            except socket.timeout:
                serv.privmsg(
                    chan, "{0}{1}[ERROR]{2} API timeout...".format(
                        self.BOLD, self.RED, self.END))
                pass


def main():

    usage = './swiss.py <start> or <screen>\n\n'\
        '<start> to run swiss in standard mode\n'\
        '<screen> to run swiss in detached screen'
    parser = optparse.OptionParser(usage=usage)
    (_, args) = parser.parse_args()
    if len(args) == 1 and (
            args[0] == 'start' or
            args[0] == 'screen' or
            args[0] == 'run'):
        bot = _swiss()
    else:
        parser.print_help()
        parser.exit(1)

    try:
        if args[0] == 'screen':
            swiss['mode'] = 'screen'
            os.system('{0} {1}/./swiss.py run'.format(
                swiss['start_bot'], os.path.dirname(
                    os.path.realpath(__file__))))
            sys.exit(1)
        bot.connect(
            network['server'], network['port'],
            network['bot_nick'], username=network['bot_name'])
        bot.start()

    except OSError as error:
        print(error)
        sys.exit(1)
    except irc.client.ServerConnectionError as error:
        print(error)
        sys.exit(1)

if __name__ == "__main__":
    main()

