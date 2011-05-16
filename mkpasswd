#!/usr/bin/python2.5

import md5
import os
import base64
import getpass

def hashPassword(pw):
    salt = os.urandom(6)
    salt_encoded = base64.b64encode(salt)
    md5_1 = md5.new(pw).digest()
    md5_2 = md5.new(md5_1 + salt).digest()
    md5_encoded = base64.b64encode(md5_2)
    return "$%s$%s" % (salt_encoded, md5_encoded)
    
if __name__ == "__main__":
    print "mkpasswd utility for pyrt"
    while True:
        password1 = getpass.getpass("Password: ")
        password2 = getpass.getpass("Again: ")
        if password1 != password2:
            print "ERROR: passwords don't match"
        else:
            break
    print hashPassword(password1)