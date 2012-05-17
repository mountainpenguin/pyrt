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

import cgi
import os
import sys
import rtorrent
import torrentHandler
import login
import system
import config

class Index:
    def __init__(self, conf=config.Config(), RT=None):
        if not RT:
            self.RT = rtorrent.rtorrent(self.Config.get("rtorrent_socket"))
        else:
            self.RT = RT
        self.Config = conf
        
    def index(self, view=None, sortby=None, reverse=None):
        if not view or view not in ["main","started","stopped","complete","incomplete","hashing","seeding","active"]:
            view = "main"
        if not sortby:
            sortby = "none"

        handler = torrentHandler.Handler()

        torrentList = self.RT.getTorrentList2(view)
        return handler.torrentHTML(torrentList, sortby, view, reverse)
