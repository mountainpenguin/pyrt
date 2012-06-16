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
import stat
import re
import urlparse
import time
import hashlib

from modules import bencode

class Directory(object):
    def __init__(self, fullpath, basename, contents):
        self.name = fullpath
        self.label = basename
        self.contents = contents
        
class File(object):
    def __init__(self, fullpath, basename, filetype):
        self.name = fullpath
        self.label = basename
        self.filetype = filetype
        
DIRECTORY = """
<ul>
    <li>
        <span class="folder">%(label)s</span><span class="fullpath">%(name)s</span>
        <ul>
            %(contents)s
        </ul>
    </li>
</ul>
"""

FILE = """
<li>
    <span class="file %(filetype)s">%(label)s</span><span class="fullpath">%(name)s</span>
</li>
"""

def handle_message(req):
    urlparams =  urlparse.parse_qs(req)
    request = urlparams.get("request") and urlparams.get("request")[0] or None
    if request == "filetree":
        rootDir = urlparams.get("rootDir") and urlparams.get("rootDir")[0] or None
        if rootDir and os.path.exists(rootDir):
            return request, getFileStruct(rootDir)
    elif request == "exists":
        path = urlparams.get("path") and urlparams.get("path")[0] or None
        if path and os.path.exists(path):
            return request, True
        elif path and not os.path.exists(path):
            return request, False
    return request, None
    
def _getFileType(fileName):
    fileType = "file_unknown"
    if fileName.lower().endswith(".avi") or fileName.lower().endswith(".mkv"):
        fileType = "file_video"
    elif fileName.lower().endswith(".rar"):
        fileType = "file_archive"
    elif "." in fileName and re.match("r\d+", fileName.lower().split(".")[-1]):
        fileType = "file_archive"
    elif fileName.lower().endswith(".nfo") or fileName.lower().endswith(".txt"):
        fileType = "file_document"
    elif fileName.lower().endswith(".iso"):
        fileType = "file_disk"
    elif "." in fileName and fileName.lower().split(".")[-1] in ["mp3", "aac", "flac", "m4a", "ogg"]:
        fileType = "file_music"
    return fileType
        
def getFileStruct(path):
    HTML = """<ul class="filetree">"""
    FILE = """
        <li><span class="filetree_item file %(filetype)s">%(name)s</span><span class="fullpath">%(fullpath)s</span></li>
    """
    OPENDIR = """
        <li><span class="filetree_item folder">%(name)s</span><span class="fullpath">%(fullpath)s</span><ul>
    """
    CLOSEDIR = """</ul></li>"""
    
    current_dir = None
    current_parents = None
    
    for dirpath, dirnames, dirfiles in os.walk(path, followlinks=True):
        currDir = dirpath.split(path)[1]
        if currDir == "":
            currDir = path
        parents = dirpath.split("/")[:-1]
        if parents[0] == '':
            parents = parents[1:]
        if current_dir != currDir:
            #have we moved up?
            if not current_parents or parents[-2] == current_parents[-1]:
                #no we've moved down
                HTML += OPENDIR % {"name" : os.path.basename(currDir), "fullpath" : dirpath}
            else:
                #ok we've moved up, how many levels?
                prev_levels_down = len(current_parents)
                cur_levels_down = len(parents)
                shared_down = 0
                for i in range(len(current_parents)):
                    if i == len(parents):
                        break
                    if current_parents[i] == parents[i]:
                        shared_down += 1
                    else:
                        break
                moved_up = len(current_parents) - shared_down
                HTML += (CLOSEDIR * (moved_up+1))
                HTML += OPENDIR % {"name" : os.path.basename(currDir), "fullpath" : dirpath}
        current_dir = currDir
        current_parents = parents
        for name in sorted(dirfiles):
            fullpath = os.path.join(dirpath, name)
            filetype = _getFileType(name)
            HTML += FILE % {"filetype":filetype, "name":name, "fullpath":fullpath}
    HTML += "</ul></li></ul>"
    
    return HTML
        
            

def createTorrent(path, announce, length, private, comment, output):
    if not os.path.isabs(path):
        path = os.path.abspath(path)
    if not os.path.exists(path):
        return
    
    if not os.path.isdir(path):
        size = os.stat(path).st_size
        pieces = ""
        #break file into pieces of length 'length' and obtain the sha1 hash
        with open(path) as src:
            read = 0
            while read <= size:
                chunk = src.read(length)
                sha1 = hashlib.sha1(chunk).digest()
                pieces += sha1
                read += length
        infoDict = {
            "name" : os.path.basename(path),
            "piece length" : length,
            "length" : size,
            "pieces" : pieces,
        }
        if private:
            infoDict["private"] = 1
    else:
        size = 0
        totalread = 0
        
        files = []
        base = os.path.basename(path)
        pre = path.split(base)[0]
        pieces = ""
        chunks = 0
        buff = ""
        for dirpath, dirnames, dirfiles in os.walk(path):
            rel = dirpath.split(pre)[1].split("/")[1:]
            for f in sorted(dirfiles):
                fp = os.path.join(dirpath, f)
                filesize = os.path.getsize(fp)
                size += filesize
                with open(fp) as src:
                    remaining = filesize
                    while remaining > 0:
                        done = 0
                        if len(buff) > 0:
                            req = length - len(buff)
                            if remaining < req:
                                #read into buff
                                part = src.read(remaining)
                                totalread += len(part)
                                buff += part
                                remaining -= remaining
                                done = 1
                            else:
                                chunks += 1
                                part = src.read(req)
                                buff += part
                                totalread += len(part)
                                remaining -= req
                                sha1 = hashlib.sha1(buff).digest()
                                pieces += sha1
                                buff = ""
                                done = 2
                        else:
                            if remaining < length:
                                #read into buff
                                part = src.read(remaining)
                                buff += part
                                totalread += len(part)
                                remaining -= remaining
                                done = 3
                            else:
                                chunks += 1
                                chunk = src.read(length)
                                totalread += len(chunk)
                                remaining -= length
                                sha1 = hashlib.sha1(chunk).digest()
                                pieces += sha1
                                done = 4
                        
                    
                files += [{
                    "path" : rel + [f],
                    "length" : filesize,
                }]
        
        if len(buff) > 0:
            chunks += 1
            sha1 = hashlib.sha1(buff).digest()
            pieces += sha1
            
        infoDict = {
            "name" : base,
            "piece length" : length,
            "files" : files,
            "pieces" : pieces,
        }
        if private:
            infoDict["private"] = 1
    
    torrent = {
        "announce": announce,
        "comment" : comment,
        "created by": "PyRT (c) 2012 mountainpenguin",
        "creation date" : int(time.time()),
        "info" : infoDict,
    }
    return bencode.bencode(torrent)