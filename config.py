#!/usr/bin/env python
# -*- coding: utf-8 -*-

wookie = {
    'bot_owner': ['Deshi'],
    'start_bot': 'screen -dmS wookie',
    'kill_bot': 'screen -X -S wookie kill',
    'mode': 'standard'
}

network = {
    'server': 'irc.hackthissite.org',
    'port': 6667,
    'SSL': False,
    'ipv6': False,
    'channels': ['#pbx', '#deshi', '#wickedradio'],
    'bot_nick': 'SwissArmy',
    'bot_name': 'Swiss Army IRC bot by Deshi & Arisance '
                '',
    'password': 'master'
}
shoutcast = {
    'server': "http://142.4.217.133:9203/stats?sid=1&mode=viewxml&page=0",
    'pull_delay': 1,
    'channels': ['#wickedradio']

}
freeswitch = {
    'server': "127.0.0.1",
              'port': 8021,
              'password': "ClueCon",
              'conference': 4224,
              'pin': 1337,
              'sip': "mud.chickenkiller.com",
              'did': "(929)223-2241",
              'channels': ['#pbx']
}

feeds = {
    'queue_delay': .5,
    'announce_delay': 5.0,
    'request_delay': 5.0,
    'announce': [''],
    'request': ['']
}

api = {
    'api_url': '',
    'authkey': ''
}

blacklist = {
    'announce': ['test1', 'test2', 'test3'],
    'request': ['test1', 'test2', 'test3']
}
