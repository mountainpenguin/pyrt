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

import os
import time
from modules import rtorrent
from modules import config
from modules import misc
import psutil
try:
    import json
except ImportError:
    import simplejson as json


class Global(object):
    def __init__(self, **kwargs):
        self.uprate = kwargs["uprate"]
        self.uptot = kwargs["uptot"]
        self.diskused = kwargs["diskused"]
        self.disktotal = kwargs["disktotal"]
        self.downrate = kwargs["downrate"]
        self.downtot = kwargs["downtot"]
        self.memused = kwargs["memused"]
        self.memtotal = kwargs["memtotal"]
        self.load1 = kwargs["load1"]
        self.load5 = kwargs["load5"]
        self.load15 = kwargs["load15"]
        self.load = (self.load1, self.load5, self.load15)
        self.uptime = kwargs["server_uptime"]
        self.throttle_up = kwargs["throttle_up"]
        self.throttle_down = kwargs["throttle_down"]


def hdd(path="/"):
    """
        Stats the root filesystem
        Inputs:
            path - optional, defaults to /
        Returns a tuple:
            index 0: the used bytes of the disk,
            index 1: total bytes of the disk
    """
    diskusage = psutil.disk_usage(path)
    return (diskusage.used, diskusage.total)


def mem():
    """
        returns a tuple:
            index 0: the used bytes of memory
            index 1: the total bytes of memory
    """
    memusage = psutil.virtual_memory()
    total = memusage.total
    used = total - memusage.available
    return (used, total)


def uptime():
    """
        returns the number of seconds since the system was booted
    """
    return int(time.time() - psutil.boot_time())


def get_global(encode_json=False):
    C = config.Config()
    RT = rtorrent.rtorrent(C.get("rtorrent_socket"))

    diskused, disktotal = hdd(C.get("root_directory"))
    memused, memtotal = mem()
    load1, load5, load15 = os.getloadavg()

    data = {
        "uprate": misc.humanSize(RT.getGlobalUpRate()),
        "downrate": misc.humanSize(RT.getGlobalDownRate()),
        "uptot": misc.humanSize(RT.getGlobalUpBytes()),
        "downtot": misc.humanSize(RT.getGlobalDownBytes()),
        "diskused": misc.humanSize(diskused),
        "disktotal": misc.humanSize(disktotal),
        "memused": misc.humanSize(memused),
        "memtotal": misc.humanSize(memtotal),
        "load1": "%.02f" % load1,
        "load5": "%.02f" % load5,
        "load15": "%.02f" % load15,
        "throttle_up": misc.humanSize(RT.getGlobalUpThrottle()),
        "throttle_down": misc.humanSize(RT.getGlobalDownThrottle()),
        "server_uptime": misc.humanTimeDiff(uptime()),
    }
    if not encode_json:
        return Global(**data)
    else:
        return json.dumps(Global(**data).__dict__)
