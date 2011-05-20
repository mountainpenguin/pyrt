#!/usr/bin/env python

import statvfs
import os
import psutil
import time
import rtorrent
import config
import torrentHandler

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
    used = psutil.used_phymem()
    total = psutil.TOTAL_PHYMEM
    return (used, total)
    
def uptime():
    """
        returns the number of seconds since the system was booted
    """
    return int(time.time() - psutil.BOOT_TIME)
    
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
        "uptime" : handler.humanTimeDiff(uptime()),
    }   