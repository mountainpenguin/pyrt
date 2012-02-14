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
        portrange = self.RT.getGlobalPortRange()
        favicons = dict([(os.path.basename(x.split(".ico")[0]), "/favicons/%s" % os.path.basename(x)) for x in glob.glob("static/favicons/*.ico")])
        maxpeers = self.RT.getGlobalMaxPeers()
        maxpeersseed = self.RT.getGlobalMaxPeersSeed()
        if maxpeersseed == -1:
            maxpeersseed = maxpeers
        definitions = {
            "config" : self.C.CONFIG,
            "throttleup" : int(float(self.RT.getGlobalUpThrottle()) / 1024) ,
            "throttledown" : int(float(self.RT.getGlobalDownThrottle()) / 1024),
            "generaldir" : self.RT.getGlobalRootPath(),
            "networkportfrom" : portrange.split("-")[0],
            "networkportto" : portrange.split("-")[1],
            "trackericons" : favicons,
            "performancemaxmemory" : int(float(self.RT.getGlobalMaxMemoryUsage())/1024/1024),
            "performancereceivebuffer" : int(float(self.RT.getGlobalReceiveBufferSize())/1024),
            "performancesendbuffer" : int(float(self.RT.getGlobalSendBufferSize())/1024),
            "performancemaxopenfiles" : self.RT.getGlobalMaxOpenFiles(),
            "performancemaxfilesize" : int(float(self.RT.getGlobalMaxFileSize())/1024/1024),
            "performancereadahead" : int(float(self.RT.getGlobalHashReadAhead())/1024/1024),
            "networksimuluploads" : self.RT.getGlobalMaxUploads(),
            "networksimuldownloads" : self.RT.getGlobalMaxDownloads(),
            "networkmaxpeers" : maxpeers,
            "networkmaxpeersseed" : maxpeersseed,
            "networkmaxopensockets" : self.RT.getGlobalMaxOpenSockets(),
            "networkmaxopenhttp" : self.RT.getGlobalMaxOpenHttp(),
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