#!/usr/bin/env python

import cgi
import os
import sys
import rtorrent
import torrentHandler
import cgitb
cgitb.enable()

form = cgi.FieldStorage()

VIEW = form.getfirst("view")
if not VIEW or VIEW not in ["main","name","started","stopped","complete","incomplete","hashing","seeding","active"]:
    VIEW = "main"
SORTBY = form.getfirst("sortby")
if not SORTBY:
    SORTBY = "none"
REVERSED = form.getfirst("reverse")
if not REVERSED:
    REVERSED = False

RT = rtorrent.rtorrent(5000)
handler = torrentHandler.Handler()

torrentList = RT.getTorrentList2(VIEW)
print handler.torrentHTML(torrentList, SORTBY, REVERSED)

