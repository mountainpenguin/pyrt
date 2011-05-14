#!/usr/bin/python2.5

import cookielib
import Cookie
import cPickle as pickle
import os
import md5
import base64

class User:
    def __init__(self, username, pass_hash, sess_id=None):
        self.username = username
        self.password = pass_hash
        self.sess_id = sess_id
        
class Login:
    def __init__(self):
        #get this from a pickled object
        self.USER = User("mountainpenguin", self.hashPassword("testing"))
        
    def checkPassword(self, username, pw):
        hash = self.USER.password
        salt = base64.b64decode(hash.split("$")[1])
        result = self.hashPassword(pw, salt=salt)
        if pw == result:
            return True
        else:
            return False
                
    def checkLogin(self, env):
        try:
            cookstr = env.get("HTTP_COOKIE")
            cookies = Cookie.SimpleCookie(cookstr)
            session_id = cookies.get("sess_id")
            if session_id == self.USER.password:
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
        
    def loginHTML(self):
        print """Content-Type : text/html\n
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
        <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
                <title>rTorrent - webUI Login</title>
                <link rel="stylesheet" href="/css/login.css">
                <!-- <script type="text/javascript" src="/javascript/login.js"></script> -->
            </head>
            <body>
                <div id="login_div">
                    <form>
                        <input type="password" value="password" name="password">
                    </form>
                </div>
            </body>
        </html>
        """