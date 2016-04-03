#!/usr/bin/env python
# -*- coding: utf-8 -*-

wookie = {
    'bot_owner': ['owners nickname'],
    'start_bot': 'screen -dmS wookie',
    'kill_bot': 'screen -X -S wookie kill',
    'mode': 'standard'
}

network = {
    'server': 'irc.server.com',
    'port': 6667,
    'SSL': False,
    'ipv6': False,
    'channels': ['#channel', '#channel', '#channel'],
    'bot_nick': 'SwissArmy',
    'bot_name': 'Swiss Army IRC bot by Deshi & Arisance '
                '',
    'password': 'nickserv password leave blank for none'
}
#change to the conference extension
conferences = [
    "4224"
]

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
