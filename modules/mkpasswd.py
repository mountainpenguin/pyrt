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