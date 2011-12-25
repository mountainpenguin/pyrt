#!/usr/bin/env python

import cgi
import os
import sys
import rtorrent
import torrentHandler
import login
import system
import config

class Index:
    def __init__(self, conf=config.Config()):
        self.Config = conf
        
    def index(self, password=None, view=None, sortby=None, reverse=None):
        if not view or view not in ["main","started","stopped","complete","incomplete","hashing","seeding","active"]:
            view = "main"
        if not sortby:
            sortby = "none"

        RT = rtorrent.rtorrent(self.Config.get("rtorrent_socket"))
        handler = torrentHandler.Handler()

        torrentList = RT.getTorrentList2(view)
        return handler.torrentHTML(torrentList, sortby, view, reverse)