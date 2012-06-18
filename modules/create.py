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
import json

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

def _getarg(urlparams, arg):
    return urlparams.get(arg) and urlparams.get(arg)[0] or None
    
def handle_message(req, writeback=None):
    urlparams =  urlparse.parse_qs(req)
    request = _getarg(urlparams, "request")
    if request == "filetree":
        rootDir = _getarg(urlparams, "rootDir")
        if rootDir and os.path.exists(rootDir):
            return request, getFileStruct(rootDir)
    elif request == "exists":
        path = _getarg(urlparams, "path")
        if path and os.path.exists(path):
            return request, True
        elif path and not os.path.exists(path):
            return request, False
    elif request == "create":
        try:
            path = str(_getarg(urlparams, "path"))
            announce = str(_getarg(urlparams, "announce"))
            piece = int(_getarg(urlparams, "piece"))
            private = int(_getarg(urlparams, "private"))
            comment = str(_getarg(urlparams, "comment"))
            output = str(_getarg(urlparams, "output"))
        except:
            return request, False
        
        torrentFile = createTorrent(path, announce, piece, private, comment, writeback)
        if not torrentFile:
            return request, False
        
        open(os.path.join("tmp", output), "w").write(torrentFile)
        return request, True, output
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
        
            

def _send(message, writeback):
    msg = {
        "request": "create",
        "response" : message,
    }
    writeback.write_message(json.dumps(msg))
    
def createTorrent(path, announce, length, private, comment, wb):
    if not os.path.isabs(path):
        path = os.path.abspath(path)
    if not os.path.exists(path):
        return
    
    if not os.path.isdir(path):
        size = os.stat(path).st_size
        pieces = ""
        #break file into pieces of length 'length' and obtain the sha1 hash
        perc_done = 0
        perc_done_lastsent = -1
        with open(path) as src:
            read = 0
            _send(perc_done, wb)
            while read <= size:
                chunk = src.read(length)
                sha1 = hashlib.sha1(chunk).digest()
                pieces += sha1
                read += length
                perc_done = (float(read) / size)*100
                if perc_done - perc_done_lastsent >= 1:
                    perc_done_lastsent = perc_done
                    _send(perc_done, wb)
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
        #get total size
        for dp, dn, df in os.walk(path, followlinks=True):
            for dff in df:
                size += os.path.getsize(os.path.join(dp, dff))
        
        totalread = 0
        perc_done = 0
        perc_done_lastsent = -1
        
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
                with open(fp) as src:
                    remaining = filesize
                    while remaining > 0:
                        if perc_done - perc_done_lastsent >= 1:
                            perc_done_lastsent = perc_done
                            _send(perc_done, wb)
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
                        perc_done = (float(totalread) / size)*100
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