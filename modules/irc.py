#!/usr/bin/env python

from modules.irclib import irclib
from modules.irclib import ircbot
from modules import websocket
from modules import remotes
import logging
import multiprocessing
import os
import signal
import json
import select
import socket
import time
import hashlib
import base64
import math
import re
import traceback

class IRCError(Exception):
    def __init__(self, value):
        self.val = value
    def __str__(self):
        return repr(self.val)
    def __repr__(self):
        return "IRCError: %s" % self.val
class SettingsError(Exception):
    def __init__(self, value):
        self.val = value
    def __str__(self):
        return repr(self.val)
    def __repr__(self):
        return "SettingsError: %s" % self.val

class RPCResponse(object):
    def __init__(self, **args):
        self.__dict__.update(args)

class _ModularBot(ircbot.SingleServerIRCBot):
    def shutdown(self, signalnum, stackframe):
        self.RPCCommand("log", "info", "IRCbot #%d: shutting down", self.PID)
        if self.IS_REGISTERED:
            self.RPCCommand("deregister", self.config.name, self.PID)

        try:
            os.remove("proc/bots/%d.pid" % self.PID)
        except:
            pass

        self.die("Received SIGTERM")
        sys.exit(0)

    def update(self):
        response = self.RPCCommand("get_filters", self.config.name)
        if response:
            try:
                unjsoned = json.loads(response.response)
                newf = []
                for f in unjsoned:
                    newf.append(re.compile(f))
                self.config.filters = newf
            except:
                self.RPCCommand("log", "error", "IRCBot #%d: recieved filter list but not JSON-encoded")

    def _OTPAuth(self):
        random_salt = base64.b64encode(os.urandom(10))
        token = "%i" % math.floor( time.time() / 10 )
        hashed_token = hashlib.sha256(token + random_salt).hexdigest()
        h1 = hashlib.sha256(self.config.auth).hexdigest()
        h2 = hashlib.sha256(h1 + hashed_token).hexdigest()
        return "$%s$%s" % (random_salt, h2)

    def RPCCommand(self, command, *args, **kwargs):
        OTPAuth = self._OTPAuth() 
        obj = {
            "command" : command,
            "arguments" : args,
            "keywords" : kwargs,
            "auth" : OTPAuth,
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
            return RPCResponse(**json.loads(resp))

    def __init__(self, net, nick, name, config, **kwargs):
        signal.signal(signal.SIGTERM, self.shutdown)
        self.IS_REGISTERED = False
        self.network = net
        self.nick = nick
        self.name = name
        self.config = config
        self.config.channel = kwargs["channel"]
        self.socket = websocket.create_connection(self.config.websocketURI)  
        self.PID = os.getpid()
        open("proc/bots/%d.pid" % self.PID, "w").write(str(self.PID))
        ircbot.SingleServerIRCBot.__init__(self, net, nick, name)

    def on_nicknameinuse(self, connection, event):
        self.RPCCommand("log", "error", "IRCbot #%d: started up, but nick '%s' is in use!", self.PID, self.nick)
        self.shutdown(None, None)

    def on_erroneusnickname(self, connection, event):
        self.RPCCommand("log", "error", "IRCbot #%d: started up, but nick '%s' is invalid", self.PID, self.nick)
        self.shutdown(None, None)

    def on_welcome(self, connection, event):
        r = self.RPCCommand("register", self.PID, self.config.name)
        if not r.response:
            self.RPCCommand("log", "warning", "IRCbot #%d: started up, but another bot is already registered!", self.PID)
            self.shutdown(None, None)
        self.IS_REGISTERED = True
        connection.join(self.config.channel)
        self.RPCCommand("log", "info", "IRCbot #%d: connected to IRC successfully", self.PID)
        if hasattr(self.config, "startup"):
            for cmd in self.config.startup:
                try:
                    if "%(settings." in cmd:
                        replacements = re.findall("\%\(settings\.(.*?)\)s", cmd)
                        fmt = {}
                        for repl in replacements:
                            fmt["settings.%s" % (repl)] = self.config[repl]
                        cmd = cmd % fmt
                    connection.send_raw(cmd)
                except:
                    self.RPCCommand("publicLog", "warning", "IRCbot #%d: command failed", self.PID)
                    self.RPCCommand("privateLog", "warning", "IRCbot #%d: command '%s' failed\n%s", self.PID, cmd, traceback.format_exc())

    def on_pubmsg(self, connection, event):
        self.update()
        self.RPCCommand("publicLog", "debug", "IRCBot #%d: message %r", self.PID, event.arguments()[0])
        try:
            for regex in self.config.filters:
                if regex.search(event.arguments()[0]):
                    idmatch = self.config.matcher.search(event.arguments()[0])
                    if idmatch:
                        torrentid = idmatch.group(1)
                        self.RPCCommand("log", "info", "IRCbot #%d: got filter match in source handler '%s' for torrentid '%s'", self.PID, self.config.name, torrentid)
                        self.RPCCommand("fetchTorrent", name=self.config.name, torrentid=torrentid)
                        return
        except:
            pass

    def on_ctcp(self, connection, event):
        pass

class Irc(object):
    def __init__(self, name, log, storage, websocketURI, auth):
        #search for storage settings
        store = storage.getRemoteByName(name)
        siteMod = remotes.getSiteMod(name)
        if not store or not siteMod:
            raise SettingsError("Nothing is stored for name '%s'" % name)

        #network, channel, and port should be stored in 'siteMod'
        #nick should be stored in 'store'

        try:
            self.network = siteMod.IRC_NETWORK
            self.port = siteMod.IRC_PORT
            self.channel = siteMod.IRC_CHANNEL
            matcher = siteMod.IRC_MATCH
        except AttributeError:
            raise SettingsError("IRC methods are not defined for name '%s'" % name)

        if "nick" not in store:
            self.nick = "pyrtBot"
        else:
            self.nick = store.nick

        if hasattr(siteMod, "IRC_COMMANDS"):
            startup = siteMod.IRC_COMMANDS
        else:
            startup = []
        self.name = "pyrt"
        self.log = log
        self.options = store
        self.options.startup = startup
        self.options.websocketURI = websocketURI
        self.options.auth = auth
        self.options.matcher = matcher
        
        self.PROC = None

    def startbot(self):
        bot = _ModularBot([(self.network, self.port)], self.nick, self.name, channel=self.channel, config=self.options)
        bot.start()

    def start(self):
        if not self.PROC:
            p = multiprocessing.Process(target=self.startbot)
            p.daemon = True
            p.start()
            self.PROC = p
            signal.signal(signal.SIGCHLD, self.report)
        else:
            raise IRCError("A bot has already been started!")
        
    def report(self, signalnum, stackframe):
        self.log.debug("SIGCHLD intercepted in PID #%d, target bot pid: %d", os.getpid(), self.PROC.pid)
        self.PROC.join(timeout=10)
