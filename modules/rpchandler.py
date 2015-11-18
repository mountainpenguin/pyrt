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

import json
import logging
import traceback
import urllib2
import random
import string
import os
from modules import remotes
from modules import bencode

class RPCHandler(object):
    def __init__(self, publog, ajax, storage):
        self.METHODS = {
            "listMethods" : self.listMethods,
            "privateLog" : self.privateLog,
            "publicLog" : self.publicLog,
            "log" : self.log,
            "test" : self.test,
            "fetchTorrent" : self.fetchTorrent,
            "register": self.register,
            "deregister" : self.deregister,
            "get_filters" : self.get_filters,
            "get_rss_filters" : self.get_rss_filters,
            "get_active_rss" : self.get_active_rss,
            "update_rss" : self.update_rss,
            "disable_rss" : self.disable_rss,
            "updatehash_rss" : self.updatehash_rss,
            "fetch_torrent_rss" : self.fetch_torrent_rss,
        }
        self.publog = publog
        self.ajax = ajax
        self.storage = storage

    def updatehash_rss(self, ID, h):
        #self.log("info", "Updated hash for feed %s", ID)
        return self.storage.updateHashRSSFeed(ID, h)

    def disable_rss(self, ID):
        return self.storage.disableRSSFeed(ID)

    def update_rss(self, ID, timestamp):
        #self.log("info", "Updated feed %s", ID)
        return self.storage.updateRSSFeed(ID, timestamp)

    def get_rss_filters(self, ID):
        if ID not in self.storage.RSS:
            return json.dumps({"error" : "No such RSS feed"})

        filter_list = []
        for fi in self.storage.RSS[ID].filters:
            filter_list.append(
                ([x.pattern for x in fi.positive],
                 [y.pattern for y in fi.negative],
                 fi.sizelim)
            )
        return filter_list

    def get_active_rss(self):
        feeds_ = filter(lambda x: x["enabled"], self.storage.getRSSFeeds())
        feeds = []
        try:
            for f in feeds_:
                fi_ = []
                for fi in f["filters"]:
                    try:
                        fi_.append(
                            ([x.pattern for x in fi.positive],
                             [y.pattern for y in fi.negative],
                             fi.sizelim)
                        )
                    except:
                        self.storage.reflowRSSFilters()

                f["filters"] = fi_
                feeds.append(f)
            return feeds

        except TypeError:
            self.storage.reflowRSSFilters()


    def get_filters(self, name):
        s = self.storage.getRemoteByName(name)
        if s:
            try:
                f = s.filters
            except AttributeError:
                f = []
            return json.dumps(
                [([x.pattern for x in z.positive],
                  [y.pattern for y in z.negative],
                  z.sizelim)
                 for z in f
                ]
            )
        else:
            return json.dumps({
                "error" : "Not registered"
            })


    def listMethods(self):
        return json.dumps(self.METHODS.keys())

    def test(self, message):
        self.log("Received message: %s", message)
        return "Hi %s, recieving you loud and clear" % message.split()[-1]

    def privateLog(self, level, *args, **kwargs):
        if level.lower() == "info":
            logging.info(*args, **kwargs)
        elif level.lower() == "warning":
            logging.warning(*args, **kwargs)
        elif level.lower() == "debug":
            logging.debug(*args, **kwargs)
        elif level.lower() == "error":
            logging.error(*args, **kwargs)
        else:
            logging.info(*args, **kwargs)

    def publicLog(self, level, *args, **kwargs):
        if level.lower() == "info":
            self.publog.info(*args, **kwargs)
        elif level.lower() == "warning":
            self.publog.warning(*args, **kwargs)
        elif level.lower() == "debug":
            self.publog.debug(*args, **kwargs)
        elif level.lower() == "error":
            self.publog.error(*args, **kwargs)
        else:
            self.publog.info(*args, **kwargs)

    def log(self, level, *args, **kwargs):
        self.publicLog(level, *args, **kwargs)
        self.privateLog(level, *args, **kwargs)

    def deregister(self, name, pid):
        resp = self.storage.deregisterBot(name, pid)
        if not resp:
            self.log("error", "%s bot tried to deregister, but no record", name)

    def register(self, pid, name):
        resp = self.storage.registerBot(pid, name)
        if resp:
            return "OK"
        else:
            return None, "Bot already running"

    def _respond(self, request, response, error):
        respDict = {
            "request":request,
            "response": response,
            "error" : error
        }
        return json.dumps(respDict)
        # return respDict

    def fetchTorrent(self, name, sizelim, **kwargs):
        site = remotes.getSiteMod(name)
        if site:
            s = site.Main(self.publog, self.ajax, self.storage)
            filename, torrent = s.fetch(kwargs["torrentid"])
            if sizelim[0] and sizelim[0] == 0:
                sizelim[0] = None
            if sizelim[1] and sizelim[1] == 0:
                sizelim[1] = None
            s.process(filename, torrent, sizelim[0], sizelim[1])
            return "OK", None
        else:
            return "ERROR", "No such handler"

    def _getTorrentSize(self, bencoded):
        if bencoded["info"].has_key("files"):
            #multifile torrent
            length = 0
            for f in bencoded["info"]["files"]:
                length += f["length"]
        else:
            #singlefile
            length = bencoded["info"]["length"]
        return length

    def fetch_torrent_rss(self, ID, alias, link, sizelim):
        lnk = urllib2.urlopen(link)
        #get filename if offered, else generate random filename
        try:
            filename = lnk.info()['Content-Disposition'].split("filename=\"")[1][:-1]
        except:
            filename = "".join([random.choice(string.letters) for x in range(20)]) + ".torrent"

        linkcontent = lnk.read()
        #check valid torrent file
        try:
            bencoded = bencode.bdecode(linkcontent)
        except bencode.BTL.BTFailure:
            self.log("error", "Error downloading from RSS feed (id: %s, alias: %s) - not a valid bencoded string", ID, alias)
            open("rss.test.torrent","w").write(linkcontent)
            return

        #check size limits
        if sizelim[0] and sizelim[0] == 0:
            sizelim[0] = None
        if sizelim[1] and sizelim[1] == 0:
            sizelim[1] = None

        size_lower, size_upper = sizelim

        length = self._getTorrentSize(bencoded)
        if size_upper and length > size_upper:
            return
        elif size_lower and length < size_lower:
            return

        target_p = os.path.join("torrents", filename)
        if os.path.exists(target_p):
            prepend = "".join([random.choice(string.letters) for x in range(5)])
            filename = "%s-%s" % (prepend, filename)
        open("torrents/%s" % (filename), "wb").write(linkcontent)
        self.ajax.load_from_rss(filename, alias, ID, start=True)

    def get_auth(self, msg):
        try:
            jsonified = json.loads(msg)
        except ValueError:
            self.log("error", "RPC: Non JSON call to RPC interface")
            return None
        else:
            if "auth" not in jsonified:
                self.log("error", "No authentication specified")
                return None
            else:
                return jsonified["auth"]

    def handle_message(self, msg):
        error = None
        response = None
        # structure must be:
        # {
        #   "command" : <string>,
        #   "arguments": <list>,
        #   "keywords": <dict>
        # }
        try:
            jsonified = json.loads(msg)
        except ValueError:
            self.log("error", "RPC: Non JSON call to RPC interface")
            error = "001 - requests must be JSON-encoded"
            return self._respond(response, error)

        if not isinstance(jsonified, dict):
            self.log("error", "RPC: call has invalid syntax")
            error = "002 - invalid syntax, dict required"
            return self._respond(response, error)

        req = ["command", "arguments", "keywords", "auth", "PID", "name"]
        for r in req:
            if not jsonified.has_key(r):
                self.log("error", "RPC: call has invalid syntax, missing key %r", r)
                error = "003 - invalid syntax, missing key %r" % r
                return self._respond(response, error)

        command = jsonified["command"]
        arguments = jsonified["arguments"]
        keywords = jsonified["keywords"]
        if command not in self.METHODS:
            self.log("error", "RPC: invalid method %r", command)
            error = "004 - invalid method %r" % command
            return self._respond(response, error)

        try:
            response = self.METHODS[command](*arguments, **keywords)
            if type(response) is tuple:
                response, error = response
        except:
            tb = traceback.format_exc()
            self.publicLog("error", "RPC: %s" % tb.strip().split("\n")[-1])
            self.privateLog("error", "RPC: traceback: %s" % tb)
            error = "005: %s" % tb.strip().split("\n")[-1]

        return self._respond(command, response, error)
