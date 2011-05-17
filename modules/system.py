#!/usr/bin/env python

import statvfs
import os
import psutil
import time

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