#!/usr/bin/env python

import config
from modules.Cheetah.Template import Template
from modules import rtorrent

import os
import glob

class Options:
    def __init__(self, conf=config.Config()):
        self.C = conf
        self.RT = rtorrent.rtorrent(self.C.get("rtorrent_socket"))
    
    def index(self):
        #PyRT:
            #change password
            #change port
            #(change theme)
        #rTorrent
            #global upload throttle
            #global download throttle
        portrange = self.RT.getPortRange()
        favicons = dict([(os.path.basename(x.split(".ico")[0]), "/favicons/%s" % os.path.basename(x)) for x in glob.glob("static/favicons/*.ico")])
        definitions = {
            "config" : self.C.CONFIG,
            "throttleup" : int(float(self.RT.getGlobalUpThrottle()) / 1024) ,
            "throttledown" : int(float(self.RT.getGlobalDownThrottle()) / 1024),
            "networkdir" : self.RT.getRootPath(),
            "networkportfrom" : portrange.split("-")[0],
            "networkportto" : portrange.split("-")[1],
            "trackericons" : favicons,
        }
        HTML = Template(file="htdocs/optionsHTML.tmpl", searchList=definitions).respond()
        
        return HTML
    
"""
    Options
    pyrt config:
        port
        host
        rtorrent_socket
        password
    rtorrent config:
        global upload throttle
        global download throttle
"""