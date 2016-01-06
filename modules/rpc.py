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

import base64
import math
import time
import hashlib
import os
import json
import socket


class RPCResponse(object):
    def __init__(self, **args):
        self.__dict__.update(args)


class RPC(object):
    def __init__(self, auth, name, sock):
        self.auth = auth
        self.name = name
        self.socket = sock

    def _OTPAuth(self):
        random_salt = base64.b64encode(os.urandom(10))
        token = "%i" % math.floor(time.time() / 120)
        hashed_token = hashlib.sha256(token + random_salt).hexdigest()
        h1 = hashlib.sha256(self.auth).hexdigest()
        h2 = hashlib.sha256(h1 + hashed_token).hexdigest()
        return "$%s$%s" % (random_salt, h2)

    def RPCCommand(self, command, *args, **kwargs):
        OTPAuth = self._OTPAuth()
        obj = {
            "command": command,
            "arguments": args,
            "keywords": kwargs,
            "PID": os.getpid(),
            "name": self.name,
            "auth": OTPAuth,
        }
        return self._ssend(json.dumps(obj))

    def _ssend(self, thing, json_encoded=False):
        if not json_encoded:
            try:
                jsoned = json.dumps(thing)
            except ValueError:
                # don't raise error here, transfer it on to the main loop
                jsoned = thing
        else:
            jsoned = thing

#        self.socket.send(thing)
        self.socket.send(jsoned)
        # block for reply
        try:
            resp = self.socket.recv()
        except socket.timeout:
            return None
        else:
            return RPCResponse(**json.loads(resp))
