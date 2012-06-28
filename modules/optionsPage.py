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

import config
from modules.Cheetah.Template import Template
from modules import rtorrent

import os
import glob

class Options:
    def __init__(self, conf=config.Config(), RT=None):
        self.C = conf
        if not RT:
            self.RT = rtorrent.rtorrent(self.C.get("rtorrent_socket"))
        else:
            self.RT = RT
    
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
            
        try:
            performancereadahead = int(float(self.RT.getGlobalHashReadAhead()))
        except:
            performancereadahead = None
            
        gmc_bool, gmc_value = self.RT.getGlobalMoveTo()
        gmc_enabled = gmc_bool and "checked" or ""
        if gmc_bool:
            gmc_hidden = ""
        else:
            gmc_hidden = "hidden"
        gmc_value = gmc_value and gmc_value or ""
        
        definitions = {
            "config" : self.C.CONFIG,
            "throttleup" : int(float(self.RT.getGlobalUpThrottle()) / 1024) ,
            "throttledown" : int(float(self.RT.getGlobalDownThrottle()) / 1024),
            "generaldir" : self.RT.getGlobalRootPath(),
            "generalmovecheckbool" : gmc_enabled,
            "generalmovecheckvalue" : gmc_value,
            "generalmovecheckhidden" : gmc_hidden,
            "networkportfrom" : portrange.split("-")[0],
            "networkportto" : portrange.split("-")[1],
            "trackericons" : favicons,
            "performancemaxmemory" : int(float(self.RT.getGlobalMaxMemoryUsage())/1024/1024),
            "performancereceivebuffer" : int(float(self.RT.getGlobalReceiveBufferSize())/1024),
            "performancesendbuffer" : int(float(self.RT.getGlobalSendBufferSize())/1024),
            "performancemaxopenfiles" : self.RT.getGlobalMaxOpenFiles(),
            "performancemaxfilesize" : int(float(self.RT.getGlobalMaxFileSize())/1024/1024),
            "performancereadahead" : performancereadahead,
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