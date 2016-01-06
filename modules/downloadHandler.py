#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import time

EXPIRES = 10  # time for a token to be unusable (tokens should be used immediately, this should prevent hotlinking, etc.)


class TokenExpired(Exception):
    def __init__(self, value):
        self.param = value

    def __str__(self):
        return repr(self.param)

    def __repr__(self):
        return "TokenError: %s" % self.param


class NoSuchToken(Exception):
    def __init__(self, value):
        self.param = value

    def __str__(self):
        return repr(self.param)

    def __repr__(self):
        return "TokenError: %s" % self.param


class Token(object):
    def __init__(self, value, path):
        self.value = value
        self.path = path
        self.timestamp = time.time()


class authStore(object):
    def __init__(self):
        self.STORE = {}

    def add(self, value, path):
        token = Token(value, path)
        self.STORE[value] = token

    def get(self, tokenval):
        self._clean()
        if tokenval in self.STORE:
            token = self.STORE[tokenval]
            # check timediff
            if time.time() - token.timestamp > EXPIRES:
                raise TokenExpired("Token %r expired" % tokenval)
            else:
                return token.path
        else:
            raise NoSuchToken("No such token %r" % tokenval)

    def _clean(self):
        cleanout = []
        for tok_val in self.STORE.keys():
            stamp = self.STORE[tok_val].timestamp
            if time.time() - stamp > EXPIRES:
                cleanout.append(tok_val)
        for val in cleanout:
            del self.STORE[val]


class downloadHandler(object):
    def __init__(self, log):
        self.log = log
        self.authStore = authStore()

    def addToken(self, auth, path):
        self.authStore.add(auth, path)

    def getPath(self, auth):
        return self.authStore.get(auth)
