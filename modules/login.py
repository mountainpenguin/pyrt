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

import cookielib
import Cookie
import cPickle as pickle
import os
import hashlib
import base64
import random
import string
import config

class User:
    def __init__(self, pass_hash, sess_id=None, testing=[]):
        self.password = pass_hash
        self.sess_id = sess_id
        self.testing = testing
        
class Login:
    def __init__(self, conf=config.Config(), log=None):
        self.C = conf
        self.Log = log
        #get this from a pickled object
        #get pyrt root dir
        try:
            self.USER = pickle.load(open(".user.pickle"))
        except:
            #self.USER = User("mountainpenguin", self.hashPassword("testing"))
            self.USER = User(self.C.CONFIG.password)
        
    def _flush(self):
        pickle.dump(self.USER, open(".user.pickle", "w"))
        
    def checkPassword(self, pw, ip):
        hash = self.USER.password
        salt = base64.b64decode(hash.split("$")[1])
        result = self.hashPassword(pw, salt=salt)
        if result == self.USER.password:
            self.Log.info("LOGIN: User successfully logged in from %s.*.*.*", ip.split(".")[0])
            return True
        else:
            self.Log.warning("LOGIN: Attempted login from %s.*.*.* failed (invalid password)", ip.split(".")[0])
            return False
                
    def checkLogin(self, cookies):
        try:
            session_id = cookies.get("sess_id").value
            #if session_id == self.USER.sess_id:
            if session_id in self.USER.testing:
                return True
            else:
                return False
        except:
            return False
        
    def hashPassword(self, pw, salt=None):
        if not salt:
            salt = os.urandom(6)
        salt_encoded = base64.b64encode(salt)
        md5_1 = hashlib.md5(pw).digest()
        md5_2 = hashlib.md5(md5_1 + salt).digest()
        md5_encoded = base64.b64encode(md5_2)
        return "$%s$%s" % (salt_encoded, md5_encoded)
        
    def loginHTML(self, msg=""):
        return """
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
        <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
                <title>rTorrent - webUI Login</title>
                <link rel="stylesheet" href="/css/main.css">
                <!-- <script type="text/javascript" src="/javascript/login.js"></script> -->
            </head>
            <body>
                <div id="login_div">
                    <div class="notice">%s</div>
                    <h1>Login to your rTorrent webUI</h1>
                    <form method="POST" action="">
                        <label>Enter Password: </label>
                        <input type="password" name="password">
                    </form>
                </div>
            </body>
        </html>
        """ % msg
        
    def sendCookie(self, getSessID=False):
        randstring = "".join([random.choice(string.letters + string.digits) for i in range(20)])
        #add sess_id to self.USER
        #self.USER.sess_id = randstring
        self.USER.testing += [randstring]
        self._flush()  
        if getSessID:
            return randstring
        new_cookie = Cookie.SimpleCookie()
        new_cookie["sess_id"] = randstring
        return new_cookie
