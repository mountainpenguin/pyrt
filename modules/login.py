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

import cPickle as pickle
import os
import hashlib
import base64
import random
import string
import time
import math
import logging
import traceback


class User(object):
    def __init__(self, pass_hash, sess_id=None, testing=[]):
        self.password = pass_hash
        self.sess_id = sess_id
        self.testing = testing


class Login:
    def __init__(self, app):
        self.C = app._pyrtConfig
        self.Log = app._pyrtLog
        self.application = app
        # get this from a pickled object
        # get pyrt root dir
        try:
            self.USER = pickle.load(open(".user.pickle"))
        except:
            self.USER = User(self.C.CONFIG.password)
        self.PERM_SALT = self.USER.password.split("$")[1]

    def _flush(self):
        pickle.dump(self.USER, open(".user.pickle", "w"))

    def _getTimeToken(self):
        return "%i" % math.floor(time.time() / 120)

    def getRPCAuth(self):
        if hasattr(self.USER, "rpcauth"):
            return self.USER.rpcauth
        else:
            # gen random
            rand = hashlib.sha256(os.urandom(20)).hexdigest()
            self.USER.rpcauth = rand
            return rand

    def checkRPCAuth(self, auth):
        try:
            rand_salt = auth.split("$")[1]
        except IndexError:
            self.Log.error("RPC: Invalid syntax in auth string")
            return False

        rpcauth = self.USER.rpcauth
        currToken = self._getTimeToken()
        token_salt = hashlib.sha256(currToken + rand_salt).hexdigest()
        h1 = hashlib.sha256(rpcauth).hexdigest()
        h2 = hashlib.sha256(h1 + token_salt).hexdigest()
        fmt = "$%s$%s" % (rand_salt, h2)
        if fmt == auth:
            return True
        else:
            return False

    def getPermSalt(self):
        return self.USER.password.split("$")[1]

    def checkPassword(self, pw, ip):
        # pw = TOTP hash
        try:
            TOTP_salt = pw.split("$")[1]
        except IndexError:
            self.Log.error("LOGIN: Invalid syntax in login attempt from %s", ip)
            logging.error("Invalid syntax in login attempt from %s", ip)
            return False
        except:
            logging.error("Unhandled error in login, traceback: %s", traceback.format_exc())
            return False

        hashed = self.USER.password
#        perm_salt = hashed.split("$")[1]
        pwhash = hashed.split("$")[2]
        currToken = self._getTimeToken()
        token_salt = hashlib.sha256(currToken + TOTP_salt).hexdigest()
        cmp_hash = hashlib.sha256(pwhash + token_salt).hexdigest()
        cmpval = "$%s$%s" % (TOTP_salt, cmp_hash)
        if pw == cmpval:
            self.Log.info("LOGIN: User successfully logged in from %s", ip)
            return True
        else:
            self.Log.warning("LOGIN: Attempted login from %s failed (invalid password)", ip)
            return False

    def checkLogin(self, session_id, ipaddr):
        try:
            salt = session_id.split("$")[1]

            h1 = hashlib.sha256(self.USER.sess_id).hexdigest()
            h2 = hashlib.sha256(h1 + ipaddr).hexdigest()
            h3 = hashlib.sha256(h2 + salt).hexdigest()
            if "$%s$%s" % (salt, h3) == session_id:
                return True
            else:
                self.Log.debug("Session for %s has expired", ipaddr)
                return False

#            for sess_id in self.USER.testing:
#                h1 = hashlib.sha256(sess_id).hexdigest()
#                h2 = hashlib.sha256(h1 + ipaddr).hexdigest()
#                h3 = hashlib.sha256(h2 + salt).hexdigest()
#                if "$%s$%s" % (salt, h3) == session_id:
#                    return True
#            self.Log.debug("Session for %s.*.*.* has expired" % ipaddr.split(".")[0])
#            return False
        except:
            return False

    def hashPassword(self, pw, salt=None):
        if not salt:
            salt = os.urandom(6)
        salt_encoded = base64.b64encode(salt)
        hash_1 = hashlib.sha256(pw).hexdigest()
        hash_2 = hashlib.sha256(hash_1 + salt_encoded).hexdigest()
        return "$%s$%s" % (salt_encoded, hash_2)

    def sendCookie(self, ipaddr):
        randstring = "".join([random.choice(string.letters + string.digits) for i in range(20)])
        # add sess_id to self.USER
        self.USER.sess_id = randstring
#        self.USER.testing += [randstring]
        self._flush()

        # hash sess_id
        h1 = hashlib.sha256(randstring).hexdigest()
        h2 = hashlib.sha256(h1 + ipaddr).hexdigest()
        rand_salt = base64.b64encode(os.urandom(10))
        h3 = hashlib.sha256(h2 + rand_salt).hexdigest()
        return "$%s$%s" % (rand_salt, h3)
