#!/usr/bin/env python

""" Copyright (C) 2012 mountainpenguin (pinguino.de.montana@googlemail.com)
    <http://github.com/mountainpenguin/pyrt>
    
    This file is part of pyRT.

    pyRT is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    pyRT is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with pyRT.  If not, see <http://www.gnu.org/licenses/>.
"""

import json
import logging
import traceback
from modules import remotes

class RPCHandler(object):
    def __init__(self, publog, ajax, storage):
        self.METHODS = {
            "listMethods" : self.listMethods,
            "privateLog" : self.privateLog,
            "publicLog" : self.publicLog,
            "log" : self.log,
            "test" : self.test,
            "fetchTorrent" : self.fetchTorrent,
            "register": self.register,
            "deregister" : self.deregister,
            "get_filters" : self.get_filters,
        }
        self.publog = publog
        self.ajax = ajax
        self.storage = storage

    def get_filters(self, name):
        s = self.storage.getRemoteByName(name)
        if s:
            try:
                f = s.filters
            except AttributeError:
                f = []

            return json.dumps([x.pattern for x in f])


    def listMethods(self):
        return json.dumps(self.METHODS.keys())

    def test(self, message):
        self.log("Received message: %s", message)
        return "Hi %s, recieving you loud and clear" % message.split()[-1]

    def privateLog(self, level, *args, **kwargs):
        if level.lower() == "info":
            logging.info(*args, **kwargs)
        elif level.lower() == "warning":
            logging.warning(*args, **kwargs)
        elif level.lower() == "debug":
            logging.debug(*args, **kwargs)
        elif level.lower() == "error":
            logging.error(*args, **kwargs)
        else:
            logging.info(*args, **kwargs)

    def publicLog(self, level, *args, **kwargs):
        if level.lower() == "info":
            self.publog.info(*args, **kwargs)
        elif level.lower() == "warning":
            self.publog.warning(*args, **kwargs)
        elif level.lower() == "debug":
            self.publog.debug(*args, **kwargs)
        elif level.lower() == "error":
            self.publog.error(*args, **kwargs)
        else:
            self.publog.info(*args, **kwargs)

    def log(self, level, *args, **kwargs):
        self.publicLog(level, *args, **kwargs)
        self.privateLog(level, *args, **kwargs)

    def deregister(self, name, pid):
        resp = self.storage.deregisterBot(name, pid)
        if not resp:
            self.log("error", "%s bot tried to deregister, but no record", name)

    def register(self, pid, name):
        resp = self.storage.registerBot(pid, name)
        if resp:
            return self._respond("OK", None)
        else:
            return self._respond(None, "Bot already running")

    def _respond(self, response, error):
        respDict = {
            "response": response,
            "error" : error
        }
        return json.dumps(respDict)
        # return respDict

    def fetchTorrent(self, name, **kwargs):
        site = remotes.getSiteMod(name)
        if site:
            s = site.Main(self.publog, self.ajax, self.storage)
            filename, torrent = s.fetch(kwargs["torrentid"]) 
            s.process(filename, torrent)
            return self._respond("OK", None)
        else:
            return self._respond("No such handler", "No such handler")

    def get_auth(self, msg):
        try:
            jsonified = json.loads(msg)
        except ValueError:
            self.log("error", "RPC: Non JSON call to RPC interface")
            return None
        else:
            if "auth" not in jsonified:
                self.log("error", "No authentication specified")
                return None
            else:
                return jsonified["auth"]

    def handle_message(self, msg):
        error = None
        response = None
        # structure must be:
        # {
        #   "command" : <string>,
        #   "arguments": <list>,
        #   "keywords": <dict>
        # }
        try:
            jsonified = json.loads(msg)
        except ValueError:
            self.log("error", "RPC: Non JSON call to RPC interface")
            error = "001 - requests must be JSON-encoded"
            return self._respond(response, error)

        if not isinstance(jsonified, dict):
            self.log("error", "RPC: call has invalid syntax")
            error = "002 - invalid syntax, dict required"
            return self._respond(response, error)

        req = ["command", "arguments", "keywords", "auth"]
        for r in req:
            if not jsonified.has_key(r):
                self.log("error", "RPC: call has invalid syntax, missing key %r", r)
                error = "003 - invalid syntax, missing key %r" % r
                return self._respond(response, error)

        command = jsonified["command"]
        arguments = jsonified["arguments"]
        keywords = jsonified["keywords"]
        if command not in self.METHODS:
            self.log("error", "RPC: invalid method %r", command)
            error = "004 - invalid method %r" % command
            return self._respond(response, error)

        try:
            response = self.METHODS[command](*arguments, **keywords)
        except:
            tb = traceback.format_exc()
            self.publicLog("error", "RPC: %s" % tb.strip().split("\n")[-1])
            self.privateLog("error", "RPC: traceback: %s" % tb)
            error = "005: %s" % tb.strip().split("\n")[-1]

        return self._respond(response, error) 
