#!/usr/bin/python2.5

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
        
class ConfigStore:
    def __init__(self, sockpath, serverhost, serverport, password):
        self.rtorrent_socket = sockpath
        self.host = serverhost
        self.port = serverport
        self.password = password
        
class Config:
    def __init__(self):
        #look for saved config file
        if os.path.exists(os.path.join("config",".pyrtconfig")):
            self.CONFIG = pickle.load(open(os.path.join("config",".pyrtconfig")))
        else:
            self.loadconfig()
    
    def _flush(self):
        pickle.dump(self.CONFIG, open(os.path.join("config",".pyrtconfig"),"w"))
        
    def loadconfig(self):
        if not os.path.exists(os.path.join("config",".pyrtrc")):
            raise ConfigError("Config File doesn't exist")
            
        config_ = open(os.path.join("config",".pyrtrc")).read()
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
            self.CONFIG = ConfigStore(
                        sockpath = configfile["rtorrent_socket"],
                        serverhost = configfile["host"],
                        serverport = configfile["port"],
                        password = configfile["password"],
                        )
            self._flush()
        except KeyError:
            raise ConfigError("Config File is malformed")
        
    def get(self, conf):
        if conf in self.CONFIG.__dict__.keys():
            return self.CONFIG.__dict__[conf]
        else:   
            return None
