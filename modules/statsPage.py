#!/usr/bin/env python

from __future__ import print_function
from modules import config
from modules import rtorrent
from modules import torrentHandler
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
        if request == "globalspeed":
            uprate = self.RT.getGlobalUpRate()
            downrate = self.RT.getGlobalDownRate()
            return json.dumps({
                "uprate" : uprate,
                "downrate" : downrate,
            })
#uprate = handler.humanSize(RT.getGlobalUpRate())
#downrate = handler.humanSize(RT.getGlobalDownRate())