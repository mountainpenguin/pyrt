#!/usr/bin/env python

from __future__ import print_function
import hashlib
import os
import base64
import getpass

def hashPassword(pw):
    salt = os.urandom(6)
    salt_encoded = base64.b64encode(salt)
    md5_1 = hashlib.md5(pw).digest()
    md5_2 = hashlib.md5(md5_1 + salt).digest()
    md5_encoded = base64.b64encode(md5_2)
    return "$%s$%s" % (salt_encoded, md5_encoded)
    
def main():
    print("mkpasswd utility for pyrt")
    while True:
        password1 = getpass.getpass("Password: ")
        password2 = getpass.getpass("Again: ")
        if password1 != password2:
            print("ERROR: passwords don't match")
        else:
            break
    print(hashPassword(password1))
    
if __name__ == "__main__":
    main()