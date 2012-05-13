#!/usr/bin/env python

from __future__ import print_function
from modules import config
from modules import rtorrent

class Index(object):
    def __init__(self, conf=config.Config(), RT=None):
        self.Config = conf
        if not RT:
            self.RT = rtorrent.rtorrent(self.Config.get("rtorrent_socket"))
        else:
            self.RT = RT
