#!/usr/bin/env python

from modules.irclib import irclib
from modules.irclib import ircbot
import logging
import multiprocessing
import os
import socket

class _Config(object):
    def __init__(self, **args):
        self.__dict__.update(args)

class _ModularBot(ircbot.SingleServerIRCBot):
    def __init__(self, net, nick, name, *args, **kwargs):
        self.config = _Config(**kwargs)
        #create unix socket for communication with tornado server

        ircbot.SingleServerIRCBot.__init__(self, net, nick, name)

    def on_welcome(self, connection, event):
        connection.join(self.config.channel)

    def on_pubmsg(self, connection, event):
        pass

class Irc(object):
    def __init__(self, log, network="127.0.0.1", channel="#mp-dev", nick="pyrtBot", port=6667):
        self.network = network
        self.port = port
        self.channel = channel
        self.nick = nick
        self.name = "pyrt"
        self.log = log

    def startbot(self):
        bot = _ModularBot([(self.network, self.port)], self.nick, self.name, channel=self.channel)
        bot.start()

    def start(self):
        p = multiprocessing.Process(target=self.startbot)
        p.daemon = True
        p.start()
