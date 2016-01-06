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
try:
    import json
except ImportError:
    import simplejson as json


class ConfigError(Exception):
    def __init__(self, value):
        self.parameter = value

    def __repr__(self):
        return repr(self.parameter)

    def __str__(self):
        return self.__repr__()


class ConfigStore(object):
    def __init__(self, sockpath, serverhost, serverport, password, ssl_certificate=None, ssl_private_key=None, ca_certs=None, root_directory="/", logfile="pyrt.log", refresh=10, scgi_username=None, scgi_password=None, scgi_method="Digest"):
        self.rtorrent_socket = sockpath
        self.host = serverhost
        self.port = serverport
        self.password = password
        self.ssl_certificate = ssl_certificate
        self.ssl_private_key = ssl_private_key
        self.ssl_ca_certs = ca_certs
        self.root_directory = root_directory
        self.logfile = logfile
        self.refresh = refresh
        self.scgi_username = scgi_username
        self.scgi_password = scgi_password
        self.scgi_method = scgi_method


class Config:
    def __init__(self):
        # look for saved config file
        if os.path.exists(os.path.join("config", ".pyrtconfig")):
            try:
                self.CONFIG = pickle.load(open(os.path.join("config", ".pyrtconfig")))
            except:
                os.remove(os.path.join("config", ".pyrtconfig"))
                self.loadconfig()
        else:
            self.loadconfig()

    def set(self, key, value):
        if key not in self.CONFIG.__dict__:
            return False
        else:
            self.CONFIG.__dict__[key] = value
            self._flush()
            return self.CONFIG.__dict__[key]

    def _flush(self):
        pickle.dump(self.CONFIG, open(os.path.join("config", ".pyrtconfig"), "w"))

    def loadconfig(self):
        if not os.path.exists(os.path.join("config", ".pyrtrc")):
            raise ConfigError("Config File doesn't exist")

        config_ = open(os.path.join("config", ".pyrtrc")).read()
        config_stripped = ""
        for line in config_.split("\n"):
            if line == "":
                pass
            else:
                for char in line:
                    if char == "#":
                        break
                    else:
                        config_stripped += char
                config_stripped += "\n"
        try:
            configfile = json.loads(config_stripped)
            if "ssl_certificate" in configfile.keys() and "ssl_private_key" in configfile.keys():
                cert = configfile["ssl_certificate"]
                pkey = configfile["ssl_private_key"]
            else:
                cert, pkey = None, None

            if "ssl_ca_certs" in configfile.keys():
                ca_certs = configfile["ssl_ca_certs"]
            else:
                ca_certs = None

            if "root_directory" in configfile:
                root_dir = configfile["root_directory"]
            else:
                root_dir = "/"

            if "logfile" in configfile:
                logfile = configfile["logfile"]
            else:
                logfile = "pyrt.log"

            try:
                refresh = int(configfile["refresh"])
            except:
                refresh = 10

            if "scgi_username" in configfile:
                scgi_username = configfile["scgi_username"]
            else:
                scgi_username = None
            if "scgi_password" in configfile:
                scgi_password = configfile["scgi_password"]
            else:
                scgi_password = None

            if "scgi_method" in configfile:
                scgi_method = configfile["scgi_method"]
            else:
                scgi_method = "Digest"

            self.CONFIG = ConfigStore(
                sockpath=configfile["rtorrent_socket"],
                serverhost=configfile["host"],
                serverport=configfile["port"],
                password=configfile["password"],
                ssl_certificate=cert,
                ssl_private_key=pkey,
                ca_certs=ca_certs,
                root_directory=root_dir,
                logfile=logfile,
                refresh=refresh,
                scgi_username=scgi_username,
                scgi_password=scgi_password,
                scgi_method=scgi_method,
            )
            self._flush()
        except KeyError:
            raise ConfigError("Config File is malformed")

    def get(self, conf):
        if conf in self.CONFIG.__dict__.keys():
            return self.CONFIG.__dict__[conf]
        else:
            return None
