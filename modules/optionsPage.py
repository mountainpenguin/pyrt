#!/usr/bin/env python

import config
from modules.Cheetah.Template import Template

class Options:
    def __init__(self, conf=config.Config()):
        self.C = conf
    
    def index(self):
        #PyRT:
            #change password
            #change port
            #(change theme)
        #rTorrent
            #global upload throttle
            #global download throttle
        definitions = {
            "pyrt_port" : self.C.get("port"),
            "config" : self.C.CONFIG,
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