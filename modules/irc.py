#!/usr/bin/env python

from modules.irclib import irclib
from modules.irclib import ircbot
import logging
import multiprocessing

class _Config(object):
    def __init__(self, **args):
        self.__dict__.update(args)

class _ModularBot(ircbot.SingleServerIRCBot):
    def __init__(self, net, nick, name, *args, **kwargs):
        self.config = _Config(**kwargs)
        ircbot.SingleServerIRCBot.__init__(self, net, nick, name)

    def on_welcome(self, connection, event):
        connection.join(self.config.channel)

    def on_pubmsg(self, connection, event):
#        self.config.log.debug("IRC: %s said %r in %s", event.source().split("!")[0], event.arguments()[0], event.target())
#        logging.info("PRIVMSG source: %s target: %s arguments: %r", event.source(), event.target(), event.arguments())
        pass

class Irc(object):
    def __init__(self, log, network="127.0.0.1", channel="#mp-dev", nick="pyrtBot", port=6667):
        self.network = network
        self.port = port
        self.channel = channel
        self.nick = nick
        self.name = "pyrt"
        self.log = log

    def start(self):
        bot = _ModularBot([(self.network, self.port)], self.nick, self.name, channel=self.channel, log=self.log)
#        p = multiprocessing.Process(target=bot.start)
#        p.daemon = True
#        p.start()
        self.log.info("IRC bot start function executed, but disabling for further dev work")
