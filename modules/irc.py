#!/usr/bin/env python

from modules.irclib import irclib
from modules.irclib import ircbot
from modules import websocket
import logging
import multiprocessing
import os
import signal
import json
import select
import socket

class _Config(object):
    def __init__(self, **args):
        self.__dict__.update(args)

class RPCResponse(object):
    def __init__(self, **args):
        self.__dict__.update(args)

class _ModularBot(ircbot.SingleServerIRCBot):
    def shutdown(self, signalnum, stackframe):
        self.die("Received SIGTERM")
        if os.path.exists("proc/bots/%d.pid" % self.PID):
            os.remove("proc/bots/%d.pid" % self.PID)
        sys.exit(0)

    def RPCCommand(self, command, *args, **kwargs):
        obj = {
            "command" : command,
            "arguments" : args,
            "keywords" : kwargs
        }
        return self._ssend(json.dumps(obj))

    def _ssend(self, thing, json_encoded=False):
        if not json_encoded:
            try:
                jsoned = json.dumps(thing)
            except ValueError:
                #don't raise error here, transfer it on to the main loop
                jsoned = thing
        else:
            jsoned = thing

        self.socket.send(thing)
        #block for reply
        self.socket.settimeout(3)
        try:
            resp = self.socket.recv()
        except socket.timeout:
            return None
        else:
            if resp != "None" and resp != "null":
                return RPCResponse(**json.loads(resp))
            else:
                return None

    def __init__(self, net, nick, name, *args, **kwargs):
        signal.signal(signal.SIGTERM, self.shutdown)
        self.network = net
        self.nick = nick
        self.name = name
        self.config = _Config(**kwargs)
        self.socket = websocket.create_connection(self.config.websocketURI)  
        self.PID = os.getpid()
        open("proc/bots/%d.pid" % self.PID, "w").write(str(self.PID))
        ircbot.SingleServerIRCBot.__init__(self, net, nick, name)

    def on_welcome(self, connection, event):
        connection.join(self.config.channel)
        self.RPCCommand("log", "debug", "IRCbot #%d: connected to IRC successfully", self.PID)

    def on_pubmsg(self, connection, event):
        self.RPCCommand("log", "debug", "IRCbot #%d: %s said '%r' in %s", self.PID, event.source().split("!")[0], event.arguments()[0], event.target())

    def on_ctcp(self, connection, event):
        pass

class Irc(object):
    def __init__(self, log, network="127.0.0.1", channel="#mp-dev", nick="pyrtBot", port=6667, **kwargs):
        self.network = network
        self.port = port
        self.channel = channel
        self.nick = nick
        self.name = "pyrt"
        self.log = log
        self.options = kwargs

    def startbot(self):
        bot = _ModularBot([(self.network, self.port)], self.nick, self.name, channel=self.channel, **self.options)
        bot.start()

    def start(self):
        p = multiprocessing.Process(target=self.startbot)
        p.daemon = True
        p.start()
