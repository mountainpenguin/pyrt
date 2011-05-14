#!/usr/bin/python2.5

import cookielib
import Cookie
import cPickle as pickle
import os
import md5
import base64
import random
import string

class User:
    def __init__(self, username, pass_hash, sess_id=None):
        self.username = username
        self.password = pass_hash
        self.sess_id = sess_id
        
class Login:
    def __init__(self):
        #get this from a pickled object
        try:
            self.USER = pickle.load(open("/home/torrent/pyrt/.user.pickle"))
        except:
            self.USER = User("mountainpenguin", self.hashPassword("testing"))
        
    def _flush(self):
        pickle.dump(self.USER, open("/home/torrent/pyrt/.user.pickle","w"))
        
    def checkPassword(self, pw):
        hash = self.USER.password
        salt = base64.b64decode(hash.split("$")[1])
        result = self.hashPassword(pw, salt=salt)
        if result == self.USER.password:
            return True
        else:
            return False
                
    def checkLogin(self, env):
        try:
            cookstr = env.get("HTTP_COOKIE")
            cookies = Cookie.SimpleCookie(cookstr)
            session_id = cookies.get("sess_id").value
            if session_id == self.USER.sess_id:
                return True
            else:
                return False
        except:
            return False
        
    def hashPassword(self, pw, salt=None):
        if not salt:
            salt = os.urandom(6)
        salt_encoded = base64.b64encode(salt)
        md5_1 = md5.new(pw).digest()
        md5_2 = md5.new(md5_1 + salt).digest()
        md5_encoded = base64.b64encode(md5_2)
        return "$%s$%s" % (salt_encoded, md5_encoded)
        
    def loginHTML(self, msg=""):
        print """Content-Type : text/html\n
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
        <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
                <title>rTorrent - webUI Login</title>
                <link rel="stylesheet" href="/css/main.css">
                <!-- <script type="text/javascript" src="/javascript/login.js"></script> -->
            </head>
            <body style="background-color : #545454;">
                <div id="login_div">
                    <h1>Login to your rTorrent webUI</h1>
                    <form method="POST" action="">
                        <div class="column-1">Enter Password: </div>
                        <div class="column-2"><input type="password" name="password"></div>
                        <div class="column-2" id="login-message">%s</div>
                    </form>
                </div>
            </body>
        </html>
        """ % msg
        
    def sendCookie(self):
        randstring = "".join([random.choice(string.letters + string.digits) for i in range(20)])
        new_cookie = Cookie.SimpleCookie()
        new_cookie["sess_id"] = randstring
        #add sess_id to self.USER
        self.USER.sess_id = randstring
        self._flush()
        print new_cookie
        