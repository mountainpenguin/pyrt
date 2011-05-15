#!/usr/bin/python2.5

import cPickle as pickle
import os
try:
    import json
except ImportError:
    import simplejson as json

def test():
    print os.getcwd()
    
class ConfigError(Exception):
    def __init__(self, value):
        self.parameter = value
        
    def __repr__(self):
        return repr(self.parameter)
        
    def __str__(self):
        return self.__repr__()
        
class ConfigStore:
    def __init__(self, sockpath, serverport):
        self.rtorrent_socket = sockpath
        self.port = serverport
        
class Config:
    def __init__(self):
        #look for saved config file
        if os.path.exists(os.path.expanduser("~/.pyrtconfig"):
            self.CONFIG = pickle.load(open(os.path.expanduser("~/.pyrtconfig")))
        else:
            self.loadconfig()
    
    def _flush(self):
        pickle.dump(self.CONFIG, open(os.path.expanduser("~/.pyrtconfig"),"w"))
        
    def loadconfig(self):
        if not os.path.exists(os.path.expanduser("~/.pyrtrc")):
            raise ConfigError("Config File doesn't exist")
            
        configfile = json.loads(open(os.path.expanduser("~/.pyrtrc")).read())
        self.CONFIG = ConfigStore(
                        sockpath = configfile["rtorrent_socket"],
                        serverport = configfile["port"],
                        )
        self._flush()
        
    def get(self, conf):
        if conf in self.CONFIG.__dict__.keys():
            return self.CONFIG.__dict__[conf]
        else:   
            return None