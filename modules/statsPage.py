#!/usr/bin/env python

from __future__ import print_function
from modules import config
from modules import rtorrent
from modules import torrentHandler
from modules import system
import os
import json

class Index(object):
    def __init__(self, conf=config.Config(), RT=None):
        self.Config = conf
        if not RT:
            self.RT = rtorrent.rtorrent(self.Config.get("rtorrent_socket"))
        else:
            self.RT = RT
        self.handler = torrentHandler.Handler()

    def handle_request(self, request):
        if request == "global":
            uprate = self.RT.getGlobalUpRate()
            downrate = self.RT.getGlobalDownRate()
            loadavg = os.getloadavg()[0]
            memusage = system.mem()
            memperc = int((float(memusage[0]) / memusage[1])*100)
            return json.dumps({
                "uprate" : uprate,
                "downrate" : downrate,
                "loadavg" : loadavg,
                "uprate_str" : self.handler.humanSize(uprate),
                "downrate_str" : self.handler.humanSize(downrate),
                "memusage" : memperc,
            })
        else:
            return "ERROR/no such method"
