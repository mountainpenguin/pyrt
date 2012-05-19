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

class RPCHandler(object):
    def __init__(self, publog):
        self.METHODS = {
            "listMethods" : self.listMethods,
            "privateLog" : self.privateLog,
            "publicLog" : self.publicLog,
            "log" : self.log,
            "test" : self.test,
        }
        self.publog = publog

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

    def _respond(self, response, error):
        respDict = {
            "response": response,
            "error" : error
        }
        return json.dumps(respDict)
        # return respDict

    def handle_message(self, msg):
        error = None
        response = None
        try:
            jsonified = json.loads(msg)
        except ValueError:
            self.log("error", "RPC: Non JSON call to RPC interface")
            error = "001 - requests must be JSON-encoded"
            return self._respond(response, error)

        # structure must be:
        # {
        #   "command" : <string>,
        #   "arguments": <list>,
        #   "keywords": <dict>
        # }
        if not isinstance(jsonified, dict):
            self.log("error", "RPC: call has invalid syntax")
            error = "002 - invalid syntax, dict required"
            return self._respond(response, error)

        req = ["command", "arguments", "keywords"]
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
