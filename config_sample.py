#!/usr/bin/env python
# -*- coding: utf-8 -*-

wookie = {
    'bot_owner': ['NickName'],
    'start_bot': 'screen -dmS wookie',
    'kill_bot': 'screen -X -S wookie kill',
    'mode': 'standard'
}

network = {
    'server': 'irc.server.org',
    'port': 6667,
    'SSL': False,
    'ipv6': False,
    'channels': ['#channel', '#channel', '#channel'],
    'bot_nick': 'SwissArmy',
    'bot_name': 'Swiss Army IRC bot by Deshi & Arisance '
                '',
    'password': 'nickservpassword'
}
shoutcast = {
    'server': "shoutcast url for stats",
    'pull_delay': 1,
    'channels': ['#channel']

}
freeswitch = {
    'server': "127.0.0.1",
              'port': 8021,
              'password': "auth password for event socket",
              'conference': 1234,
              'pin': 1234,
              'sip': "sip address",
              'did': "(xxx)xxx-xxxx",
              'channels': ['#channel']
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
