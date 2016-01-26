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

from __future__ import print_function
from modules import irc
from modules import remotes
from modules import misc

import urlparse
import logging
import json
import re
import traceback
import os
import signal


class AutoHandler(object):
    def __init__(self, app):
        self.application = app
        self.LOGIN = app._pyrtL
        self.LOG = app._pyrtLog
        self.STORE = app._pyrtRemoteStorage
        self.METHODS = {
            "get_sources": self.get_sources,
            "get_source_single": self.get_source_single,
            "set_source": self.set_source,
            "start_bot": self.start_bot,
            "stop_bot": self.stop_bot,
            "get_filters": self.get_filters,
            "add_filter": self.add_filter,
            "remove_filter": self.remove_filter,
            "get_rss": self.get_rss,
            "add_rss": self.add_rss,
            "remove_rss": self.remove_rss,
            "enable_rss": self.enable_rss,
            "disable_rss": self.disable_rss,
            "add_rss_filter": self.add_rss_filter,
            "remove_rss_filter": self.remove_rss_filter,
            "get_rss_single": self.get_rss_single,
            "get_rss_filters": self.get_rss_filters,
        }

    def _response(self, name, request, response, error):
        return json.dumps({
            "name": name,
            "request": request,
            "response": response,
            "error": error,
        })

    def stop_bot(self, name):
        botpid = self.STORE.isBotActive(name)
        if botpid:
            # release socket
            socknum = self.STORE.assigneeSocket(name)
            if self.STORE.releaseSocket(socknum, name):
                self.LOG.info("Released RPC socket number %i" % socknum)
            else:
                self.LOG.error("Could not release RPC socket number %i" % socknum)
            try:
                os.kill(botpid, signal.SIGTERM)
                # deregister bot
                self.STORE.deregisterBot(name, botpid)
                return self._response(name, "stop_bot", "OK", None)
            except OSError:
                self.STORE.deregisterBot(name, botpid)
                return self._response(name, "stop_bot", "ERROR", "Bot is not active")
        else:
            return self._response(name, "stop_bot", "ERROR", "Bot not active")

    def start_bot(self, name):
        auth = self.LOGIN.getRPCAuth()
        botpid = self.STORE.isBotActive(name)
        if botpid:
            return self._response(name, "start_bot", "ERROR", "Bot already active")
        try:
            # get websocketURI
            socknum = self.STORE.getFreeSocket()
            ircobj = irc.Irc(name, self.LOG, self.STORE, websocketURI=".sockets/rpc%i.interface" % (socknum), auth=auth)
            p = ircobj.start()
            self.STORE.saveProc(name, p.pid, p)
            self.STORE.assignSocket(socknum, name, p)
            self.LOG.info("RPC socket number %i assigned to %s IRCbot", socknum, name)
        except:
            tb = traceback.format_exc()
            tb_line = tb.strip().split("\n")[-1]
            self.LOG.error("AUTO: error starting IRC bot for handler '%s' - %s", name, tb_line)
            logging.error(tb)
            return self._response(name, "start_bot", "ERROR", tb_line)
        else:
            return self._response(name, "start_bot", "OK", None)

    def get_source_single(self, select):
        sources = filter(
            lambda x: x[0].upper() == select.upper(),
            remotes.searchSites(),
        )
        if sources:
            source = sources[0]
            site = self.retrieve_sources(sources)[0]
            return self._response(source[0], "get_source_single", site, None)
        else:
            return self._response(select, "get_source_single", "ERROR", "Remote name '%r' not known" % select)
        return self._response(select, "get_source_single", "ERROR", "No remotes defined")

    def _get_status(self, name):
        botpid = self.STORE.isBotActive(name)
        if botpid:
            return "on"
        else:
            return "off"

    def retrieve_sources(self, sources):
        sites = []
        if sources:
            for name, desc, req, methods in sources:
                # determine if bot is running
                if "IRC" in methods:
                    status = self._get_status(name)
                    if status == "off":
                        botstatus = {
                            "img": "on.png",
                            "msg": "Start IRC",
                            "str": "start",
                        }
                    else:
                        botstatus = {
                            "img": "off.png",
                            "msg": "Stop IRC",
                            "str": "stop",
                        }

                    # fetch filters
                    s = self.STORE.getRemoteByName(name)
                    if s:
                        req_ = []
                        for r in req:
                            if r[0] in s.keys():
                                req_.append((r[0], s[r[0]]))
                            else:
                                req_.append(r)
                        req = req_
                        filters = self.get_filters(name, internal=True)
                    else:
                        filters = []

                    lookup = {
                        "name": name,
                        "desc": desc,
                        "status": status,
                        "botstatus": botstatus,
                        "keys": req,
                        "filters": filters,
                        "humanSize": misc.humanSize,
                    }
                    sites.append(self.application._pyrtTemplate.load(
                        "auto-irc-source.html"
                    ).generate(**lookup))
        return sites

    def get_sources(self):
        sources = remotes.searchSites()
        sites = self.retrieve_sources(sources)
        return self._response(None, "get_sources", sites, None)

    def get_filters(self, name, internal=False):
        s = self.STORE.getRemoteByName(name)
        if not s and not internal:
            return self._response(name, "get_filters", "ERROR", "No store for name '%s'" % name)
        elif not s and internal:
            return []

        try:
            f = s.filters
        except AttributeError:
            f = []

        if not internal:
            return self._response(name, "get_filters", [x.pattern for x in f], None)
        else:
            return f

    def _wildcardToRegex(self, restring):
        """Converts a wildcard string into a valid regular expression

           e.g. ?atch* => .atch.*
           e.g. .atch* => \.atch.*
        """
        escaped = re.escape(restring)
        return re.compile(escaped.replace("\?", ".").replace("\*", ".*"), re.I)

    def add_filter(self, name, regex, positive=[], negative=[], sizelim=None):
        regex = (regex[0] == "true")
        name = name[0]
        if positive:
            positive = positive[0].split("||||||")
        if negative:
            negative = negative[0].split("||||||")
        if sizelim:
            try:
                sizelim = [int(x) for x in sizelim[0].split("||||||")]
            except:
                return self._response(name, "add_filter", "ERROR", "Size limits must be integers")
            else:
                if sizelim[1] != 0 and sizelim[1] < sizelim[0]:
                    return self._response(name, "add_filter", "ERROR", "Upper size limit is less than the lower limit")
        else:
            sizelim = [None, None]

        s = self.STORE.getRemoteByName(name)
        if not s:
            return self._response(name, "add_filter", "ERROR", "No store for name '%s'" % name)

        # attempt to compile the re string
        positives = []
        negatives = []
        for restring in positive:
            try:
                if regex:
                    regextest = re.compile(restring)
                else:
                    regextest = self._wildcardToRegex(restring)
                positives.append(regextest)
            except:
                return self._response(name, "add_filter", "ERROR", "Invalid regex %r" % restring)

        for restring in negative:
            try:
                if regex:
                    regextest = re.compile(restring)
                else:
                    regextest = self._wildcardToRegex(restring)
                negatives.append(regextest)
            except:
                return self._response(name, "add_filter", "ERROR", "Invalid regex %r" % restring)

        if self.STORE.addFilter(name, positives, negatives, sizelim):
            return self._response(name, "add_filter", "OK", None)
        else:
            return self._response(name, "add_filter", "ERROR", "Unknown error")

    def remove_filter(self, name, index):
        name = name[0]
        try:
            index = int(index[0])
        except ValueError:
            return self._response(name, "remove_filter", "ERROR", "Not an integer")

        r = self.STORE.removeFilter(name, index)
        if r:
            return self._response(name, "remove_filter", "OK", None)
        else:
            return self._response(name, "remove_filter", "ERROR", "No such filter index")

    def set_source(self, **kwargs):
        settings = {
        }
        for k, v in kwargs.iteritems():
            if k == "auth":
                pass
            else:
                settings[k] = v[0]
        if "name" not in settings:
            return self._response(None, "set_source", "ERROR", "No remote 'name' provided")

        name = self.STORE.addRemote(**settings)
        if name:
            self.LOG.info("New remote added: '%s'" % name)
            return self._response(name, "set_source", "OK", None)
        else:
            self.LOG.error("Error in adding remote: '%s'" % name)
            return self._response(name, "set_source", "ERROR", "Unknown error")

    def get_rss(self, **kwargs):
        feeds_ = self.STORE.getRSSFeeds()
        feeds = []
        for f in feeds_:
            feeds.append(self.application._pyrtTemplate.load("auto-rss-source.html").generate(
                humanSize=misc.humanSize, **f
            ))
        return self._response("RSS", "get_rss", feeds, None)

    def get_rss_single(self, ID):
        ID = ID[0]
        resp = self.STORE.getRSSFeed(ID)
        if resp:
            feed = self.application._pyrtTemplate.load("auto-rss-source.html").generate(
                humanSize=misc.humanSize, **resp
            )
            return self._response(ID, "get_rss_single", feed, None)
        else:
            return self._response(ID, "get_rss_single", "ERROR", "No such RSS feed")

    def add_rss(self, alias=None, ttl=None, uri=None):
        if not alias or not ttl or not uri:
            raise remotes.UndefinedError("Insufficient arguments")
        try:
            uri = uri[0]
            ttl = ttl[0]
            alias = alias[0]
            self.STORE.addRSSFeed(uri, ttl, alias)
        except:
            err = traceback.format_exc()
            errsh = err.strip().split("\n")[-1]
            self.LOG.error("ERROR in autohandler (add_rss): %s", errsh)
            logging.error("ERROR in autohandler (add_rss)\n%s", err)
            return self._response("RSS", "add_rss", "ERROR", errsh)
        else:
            return self._response("RSS", "add_rss", "OK", None)

    def remove_rss(self, ID):
        if type(ID) is list:
            ID = ID[0]
        resp = self.STORE.removeRSSFeed(ID)
        if resp:
            return self._response(ID, "remove_rss", "OK", None)
        else:
            return self._response(ID, "remove_rss", "ERROR", "No such RSS feed")

    def enable_rss(self, ID):
        if type(ID) is list:
            ID = ID[0]
        resp = self.STORE.enableRSSFeed(ID)
        if resp:
            return self._response(ID, "enable_rss", "OK", None)
        else:
            return self._response(ID, "enable_rss", "ERROR", "No such RSS feed")

    def disable_rss(self, ID):
        if type(ID) is list:
            ID = ID[0]
        resp = self.STORE.disableRSSFeed(ID)
        if resp:
            return self._response(ID, "enable_rss", "OK", None)
        else:
            return self._response(ID, "enable_rss", "ERROR", "No such RSS feed")

    def add_rss_filter(self, ID, regex, positive=[], negative=[], sizelim=None):
        regex = (regex[0] == "true")
        ID = ID[0]
        if positive:
            positive = positive[0].split("||||||")
        if negative:
            negative = negative[0].split("||||||")
        if sizelim:
            try:
                sizelim = [int(x) for x in sizelim[0].split("||||||")]
            except:
                return self._response(ID, "add_filter", "ERROR", "Size limits must be integers")
            else:
                if sizelim[1] != 0 and sizelim[1] < sizelim[0]:
                    return self._response(ID, "add_filter", "ERROR", "Upper size limit is less than the lower limit")
        else:
            sizelim = [None, None]

        positives = []
        negatives = []
        for restring in positive:
            try:
                if regex:
                    regextest = re.compile(restring)
                else:
                    regextest = self._wildcardToRegex(restring)
                positives.append(regextest)
            except:
                return self._response(ID, "add_rss_filter", "ERROR", "Invalid regex %r" % restring)

        for restring in negative:
            try:
                if regex:
                    regextest = re.compile(restring)
                else:
                    regextest = self._wildcardToRegex(restring)
                negatives.append(regextest)
            except:
                return self._response(ID, "add_rss_filter", "ERROR", "Invalid regex %r" % restring)

        if self.STORE.addRSSFilter(ID, positives, negatives, sizelim):
            return self._response(ID, "add_rss_filter", "OK", None)
        else:
            return self._response(ID, "add_rss_filter", "ERROR", "Unknown Error")

    def remove_rss_filter(self, ID, index):
        ID = ID[0]
        try:
            index = int(index[0])
        except ValueError:
            return self._response(ID, "remove_rss_filter", "ERROR", "Index must be an integer")

        resp = self.STORE.removeRSSFilter(ID, index)
        if resp:
            return self._response(ID, "remove_rss_filter", "OK", None)
        elif resp is False:
            return self._response(ID, "remove_rss_filter", "ERROR", "No such RSS feed")
        elif resp is None:
            return self._response(ID, "remove_rss_filter", "ERROR", "No such filter index")

    def get_rss_filters(self, ID):
        ID = ID[0]
        resp = self.STORE.getRSSFilters(ID)
        if resp:
            return self._response(ID, "get_rss_filters", resp, None)
        else:
            return self._response(ID, "get_rss_filters", "ERROR", "No such RSS feed")

    def handle_message(self, message):
        urlparams = urlparse.parse_qs(message)
        request = urlparams.get("request") and urlparams.get("request")[0] or None
        arguments = urlparams.get("arguments") or []
        # parse for keywords (not 'request', and not 'arguments')

        def _miniCheck(arg):
            if arg[0] == "request" or arg[0] == "arguments":
                return False
            else:
                return True

        keywords = dict(filter(_miniCheck, urlparams.items()))
        if not request:
            logging.info("autoSocket: no request specified")
            return self._response(None, message, "ERROR", "No request specified")
        elif request not in self.METHODS:
            logging.info("autoSocket: request '%r' is not supported", request)
            return self._response(None, request, "ERROR", "Request '%r' is not supported" % request)
        else:
            return self.METHODS[request](*arguments, **keywords)
