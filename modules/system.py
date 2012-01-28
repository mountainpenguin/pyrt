#!/usr/bin/env python

import statvfs
import os
import time
import rtorrent
import config
import torrentHandler
import re
try:
    import json
except ImportError:
    import simplejson as json

class Global(object):
    def __init__(self, kwargs):
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
        self.cpuusage = kwargs["cpuusage"]
    
def hdd(path="/"):
    """
        Stats the root filesystem
        Inputs:
            path - optional, defaults to /
        Returns a tuple:
            index 0 : the used bytes of the disk,
            index 1 : total bytes of the disk
    """
    usage = os.statvfs(path)
    total = usage[statvfs.F_BLOCKS]
    free = usage[statvfs.F_BFREE]
    used = total - free
    block_size = usage[statvfs.F_BSIZE]
    
    return (used*block_size, total*block_size)
    
def mem():
    """
        returns a tuple:
            index 0 : the used bytes of memory
            index 1 : the total bytes of memory
    """
    
    if os.path.exists("/proc/meminfo"):
        meminfofile = open("/proc/meminfo")
        meminfo = meminfofile.read()
        meminfofile.close()
        try:
            total = int(re.search("MemTotal:.*?(\d+) kB", meminfo).group(1))*1024
            free = int(re.search("MemFree:.*?(\d+) kB", meminfo).group(1))*1024
            used = total-free
        except:
            return (0, 0)
      
    else:
        meminfofile = os.popen('vm_stat')
        meminfo = meminfofile.read()
        meminfofile.close()
        try:
            free = int(re.search("Pages free: .*?(\d+)", meminfo).group(1)) * 4096
            active = int(re.search("Pages active: .*?(\d+)", meminfo).group(1)) * 4096 
            inactive = int(re.search("Pages inactive: .*?(\d+)", meminfo).group(1)) * 4096
            wired = int(re.search("Pages wired down: .*?(\d+)", meminfo).group(1)) * 4096
            used = active + inactive + wired
            total = used + free
        except:
            return (0, 0)
    return (used, total)
    
def uptime():
    """
        returns the number of seconds since the system was booted
    """
    if os.path.exists("/proc/stat"):
        boot_time_match = re.search("btime (\d+)", open("/proc/stat").read())
        if boot_time_match:
            boot_time = int(boot_time_match.group(1))
    else:
      boot_time = int(10)
    handler = torrentHandler.Handler()
    return handler.humanTimeDiff(int(time.time() - boot_time))
    
def get_global(encode_json=False):
    C = config.Config()
    RT = rtorrent.rtorrent(C.get("rtorrent_socket"))
    handler = torrentHandler.Handler()
    
    diskused, disktotal = hdd()
    memused, memtotal = mem()
    load1, load5, load15 = os.getloadavg()
    
    uprate = handler.humanSize(RT.getGlobalUpRate())
    downrate = handler.humanSize(RT.getGlobalDownRate())
    uptot = handler.humanSize(RT.getGlobalUpBytes())
    downtot = handler.humanSize(RT.getGlobalDownBytes())
    diskused = handler.humanSize(diskused)
    disktotal = handler.humanSize(disktotal)
    memused = handler.humanSize(memused)
    memtotal = handler.humanSize(memtotal)
    load1 = "%.02f" % load1
    load5 = "%.02f" % load5
    load15 = "%.02f" % load15
    cpuusage = "None"
    server_uptime = str(uptime())
    
    if not encode_json:
        return Global(locals())
    else:
        return json.dumps(Global(locals()).__dict__)
        
def generalHTML():
    C = config.Config()
    RT = rtorrent.rtorrent(C.get("rtorrent_socket"))
    handler = torrentHandler.Handler()
    
    diskused, disktotal = hdd()
    memused, memtotal = mem()
    load1, load5, load15 = os.getloadavg()
    return """
                        <h2>Global Stats</h2>
                        <div class="column-1">Upload Rate:</div><div class="column-2">%(uprate)s/s</div>
                        <div class="column-3">Total Up:</div><div class="column-4">%(uptot)s</div>
                        <div class="column-5">Disk Usage:</div><div class="column-6">%(diskused)s / %(disktotal)s</div>
                        
                        <div class="column-1">Download Rate:</div><div class="column-2">%(downrate)s/s</div>
                        <div class="column-3">Total Down:</div><div class="column-4">%(downtot)s</div>
                        <div class="column-5">Mem Usage:</div><div class="column-6">%(memused)s / %(memtotal)s</div>
                        
                        <div class="column-1">Load Average:</div>
                        <div class="column-2">
                            <span title="Last minute">%(load1)s</span>,
                            <span title="Last 5 minutes">%(load5)s</span>,
                            <span title="Last 15 minutes">%(load15)s</span>
                        </div>
                        <div class="column-3">Uptime:</div><div class="column-4">%(uptime)s</div>
                        <div class="column-5">CPU Usage:</div><div class="column-6">%(cpuusage)s%%</div>
    """ % {
        "uprate" : handler.humanSize(RT.getGlobalUpRate()),
        "downrate" : handler.humanSize(RT.getGlobalDownRate()),
        "uptot" : handler.humanSize(RT.getGlobalUpBytes()),
        "downtot" : handler.humanSize(RT.getGlobalDownBytes()),
        "diskused" : handler.humanSize(diskused),
        "disktotal" : handler.humanSize(disktotal),
        "memused" : handler.humanSize(memused),
        "memtotal" : handler.humanSize(memtotal),
        "load1" : "%.02f" % load1,
        "load5" : "%.02f" % load5,
        "load15" : "%.02f" % load15,
        "cpuusage" : "None",
        "uptime" : str(uptime()),
    }   
