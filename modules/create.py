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
        
def getFileStruct(root):
    data = _getFileStruct(root)
    HTML = """<ul class='filetree'>
    <li><span class="folder">%s</span><span class="fullpath">%s</span>
        <ul>
    """ % (root, root)
    for item in data:
        if isinstance(item, Directory):
            HTML += DIRECTORY % {
                "label" : item.label,
                "name" : item.name,
                "contents" : _htmlify(item),
            }
        elif isinstance(item, File):
            HTML += FILE % item.__dict__
    HTML += "</ul></li></ul>"
    return HTML
            

def _htmlify(folder):
    HTML = ""
    for item in folder.contents:
        if isinstance(item, Directory):
            HTML += _htmlify(item)
        elif isinstance(item, File):
            HTML += FILE % item.__dict__
    return HTML
    
def _getFileStruct(dire):
    contents = []
    for file_ in sorted(os.listdir(dire)):
        path = os.path.join(dire, file_)
        if os.path.isdir(path):
            contents += [Directory(path, file_, _getFileStruct(path))]
        elif os.path.islink(path):
            pass
        elif stat.S_ISSOCK(os.stat(path).st_mode):
            pass
        else:
            contents += [File(path, file_, _getFileType(file_))]
    return contents

def createTorrent(path, announce, length, private, comment, output):
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
        
        files = []
        base = os.path.basename(path)
        pre = path.split(base)[0]
        print base
        print pre
        for dirpath, dirnames, dirfiles in os.walk(path):
            rel = dirpath.split(pre)[1].split("/")
            for f in dirfiles:
                s = os.stat(os.path.join(dirpath, f)).st_size
                size += s
                files += [{
                    "path" : rel + [f],
                    "length" : s,
                }]
        
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
        "creation date" : str(time.time()),
        "info" : infoDict,
    }
    return bencode.bencode(torrent)


#{
#    'announce': 'http://tracker.site1.com/announce',
#    'info:
#    {
#        'name': 'directoryName',
#        'piece length': 262144,
#        'files':
#        [
#            {'path': '111.txt', 'length': 111},
#            {'path': '222.txt', 'length': 222}
#        ],
#        'pieces': '6a8af7eda90ba9f851831073c48ea6b7b7e9feeb...8a43d9d965a47f75488d3fb47d2c586337a20b9f'
#    }
#}