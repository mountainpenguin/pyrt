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

    def _fmt_source(self, name, desc, status):
        fmt = {
            "name": name,
            "desc": desc,
            "status": status,
        }
        row_templ = "<tr class='remote_row' id='remote_name_%(name)s'><td class='name'>%(name)s</td><td class='desc'>%(desc)s</td><td class='status status-%(status)s status-%(name)s'>%(status)s</td></tr>"
        return row_templ % fmt

    def _fmt_keys(self, name, keys, filters, botcontrol):
        input_templ = "<label for='%(key)s'>%(key)s:</label><input type='text' name='%(key)s' placeholder='%(desc)s'>"
        fmt = {
            "name": name,
            "form": "".join([input_templ % {"key": x[0], "desc": x[1]} for x in keys]),
            "filters": filters,
            "botbutton": botcontrol,
        }
        row_templ = """
            <tr class='is_hidden remote_setting' id='remote_settings_%(name)s'>
                <td colspan=10>
                    <div class="settings">
                        <h4>Settings</h4>
                            %(form)s
                        <div class="submit_buttons">
                            <button type="submit" class="submit_button" id="submit_%(name)s">
                                <img src="images/submit.png" width=20 height=20>
                                <span>Submit</span>
                            </button>
                            %(botbutton)s
                        </div>
                    </div>
                    %(filters)s
                </td>
            </tr>
        """
        return row_templ % fmt

    def _fmt_subgroup(self, pos, neg, sizelim):
        filter_pos = "<div class='filter_positive filter'><code>%s</code></div>"
        filter_neg = "<div class='filter_negative filter'><code>%s</code></div>"
        filter_size = "<div class='filter_size filter'><code>%s</code></div>"
        subfilters = []
        for regex in pos:
            subfilters += [filter_pos % regex.pattern]
        for regex in neg:
            subfilters += [filter_neg % regex.pattern]
        if sizelim[0] or sizelim[1]:
            if not sizelim[1]:
                sizestring = ">%s" % misc.humanSize(sizelim[0])
            elif not sizelim[0]:
                sizestring = "<%s" % misc.humanSize(sizelim[1])
            else:
                sizestring = "%s - %s" % (misc.humanSize(sizelim[0]), misc.humanSize(sizelim[1]))
            subfilters += [filter_size % sizestring]
        return subfilters

    def _fmt_filters(self, filters):
        filter_templ = """
            <label for='filter%(count)d'>Filter:</label>
            <div name='filter%(count)d' class='filter_group'>
                %(subfilters)s
            </div>
        """
        filters_fmtted = []
        idx = 0

        try:
            for f_obj in filters:
                subfilters = self._fmt_subgroup(f_obj.positive, f_obj.negative, f_obj.sizelim)
                filters_fmtted += [
                    filter_templ % {
                        "count": idx + 1,
                        "subfilters": "".join(subfilters)
                    }
                ]
                idx += 1
        except (TypeError, AttributeError):
            self.STORE.reflowFilters()
            filters_fmtted = ["<div class='filter'>Refresh Page</div>"]

        fmt = {
            "filters": "".join(filters_fmtted),
        }
        templ = """
            <div class="filters">
                <h4>Filters</h4>
                %(filters)s
                <div class="add_filter_div">
                    <label for="add_filter">
                        <button class="add_filter_button">Add Filter</button>
                    </label>
                    <div class="add_filter">
                        <div class="regex_checkbox_parent">
                            <span class="regex_checkbox_label">Regex?</span>
                            <input type="checkbox" class="regex_checkbox" checked=1>
                        </div>
                        <input name="add_filter" class="input_filter" type="text" placeholder="Filter">
                        <select class="filter_select">
                            <option selected="selected">---</option>
                            <option value="and">and</option>
                            <option value="not">not</option>
                            <option value="size">size</option>
                        </select>
                    </div>
                </div>
            </div>
        """
        return templ % fmt

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
        sources = remotes.searchSites()
        if sources:
            for name, desc, req, methods in sources:
                if name.upper() != select.upper():
                    continue
                # determine if bot is running
                if "IRC" in methods:
                    status = self._get_status(name)
                    if status == "off":
                        statusimage = "on.png"
                        startstopmsg = "Start IRC"
                        startstop = "start"
                    else:
                        statusimage = "off.png"
                        startstopmsg = "Stop IRC"
                        startstop = "stop"

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
                        filters = self._fmt_filters(filters)
                        botcontrol = """
                            <button class="bot_button" id="%(startstop)s_%(name)s">
                                <img src="images/%(statusimage)s" width=20 height=20>
                                <span>%(startstopmsg)s</span>
                            </button>
                        """ % {"statusimage": statusimage, "startstop": startstop, "startstopmsg": startstopmsg, "name": name}
                    else:
                        filters = ""
                        botcontrol = ""

                    return self._response(name, "get_source_single", {
                        "row": self._fmt_source(name, desc, status),
                        "requirements": req,
                        "req_row": self._fmt_keys(name, req, filters, botcontrol),
                    }, None)
                else:
                    return self._response(name, "get_source_single", "ERROR", "IRC not specified as a valid method")
            return self._response(select, "get_source_single", "ERROR", "Remote name '%r' not known" % select)
        return self._response(select, "get_source_single", "ERROR", "No remotes defined")

    def _get_status(self, name):
        botpid = self.STORE.isBotActive(name)
        if botpid:
            return "on"
        else:
            return "off"

    def get_sources(self):
        sources = remotes.searchSites()
        sites = []
        if sources:
            for name, desc, req, methods in sources:
                # determine if bot is running
                if "IRC" in methods:
                    status = self._get_status(name)
                    if status == "off":
                        statusimage = "on.png"
                        startstopmsg = "Start IRC"
                        startstop = "start"

                    else:
                        statusimage = "off.png"
                        startstopmsg = "Stop IRC"
                        startstop = "stop"

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
                        filters = self._fmt_filters(filters)
                        botcontrol = """
                            <button class="bot_button" id="%(startstop)s_%(name)s">
                                <img src="images/%(statusimage)s" width=20 height=20>
                                <span>%(startstopmsg)s</span>
                            </button>
                        """ % {"statusimage": statusimage, "startstop": startstop, "startstopmsg": startstopmsg, "name": name}
                    else:
                        filters = ""
                        botcontrol = ""

                    sites.append({
                        "row": self._fmt_source(name, desc, status),
                        "requirements": req,
                        "req_row": self._fmt_keys(name, req, filters, botcontrol),
                    })
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

    def _fmt_feed(self, feed):
        templ = """
            <tr class='remote_row' id='feed_id_%(id)s'>
                <td class='enabled feed_enabled_%(enabled)s'></td>
                <td class='alias'>%(alias)s</td>
                <td class='ttl'>%(ttl_str)s</td>
                <td class='url' title='%(url)s'>%(url)s</td>
            </tr>""" % feed
        filter_templ = """
            <label for='filter%(count)d'>Filter:</label>
            <div name='filter%(count)d' class='filter_group'>
                %(subfilters)s
            </div>
        """

        # check if `filters` is in correct format

        filters_fmtted = []
        idx = 0
        try:
            for f_obj in feed["filters"]:
                subfilters = self._fmt_subgroup(f_obj.positive, f_obj.negative, f_obj.sizelim)
                filters_fmtted += [
                    filter_templ % {
                        "count": idx + 1,
                        "subfilters": "".join(subfilters)
                    }
                ]
                idx += 1
        except TypeError:
            self.STORE.reflowRSSFilters()
            filters_fmtted = ["<div class='filter'>Refresh Page</div>"]

        feed["filters"] = "".join(filters_fmtted)

        sub_templ = """
            <tr class='hidden remote_setting' id='feed_%(id)s'>
                <td colspan=10>
                    <div class='rss_controls'>
                        <img class='rss_%(enabled_str)s rss_status' src='%(enabled_image)s' alt='%(enabled_str)s' title='%(enabled_str)s' width=48 height=48>
                        <img class='rss_delete' src='images/delete48.png' alt='delete' title='Delete' width=48 height=48'>
                    </div>
                    <div class='filters'>
                        <h4>Filters</h4>
                        %(filters)s
                        <div class='add_filter_div'>
                            <label for='add_filter'>
                                <button class='add_filter_button'>Add Filter</button>
                            </label>
                            <div class="add_filter">
                                <div class="regex_checkbox_parent">
                                    <span class="regex_checkbox_label">Regex?</span>
                                    <input type="checkbox" class="regex_checkbox" checked=1>
                                </div>
                                <input name="add_filter" class="input_filter" type="text" placeholder="Filter">
                                <select class="filter_select">
                                    <option selected="selected">---</option>
                                    <option value="and">and</option>
                                    <option value="not">not</option>
                                    <option value="size">size</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </td>
            </tr>
        """ % feed
        return [templ.replace("\t", "").replace("\n", ""), sub_templ.replace("\t", "").replace("\n", "")]

    def get_rss(self, **kwargs):
        feeds_ = self.STORE.getRSSFeeds()
        feeds = []
        for f in feeds_:
            feeds.extend(self._fmt_feed(f))
        return self._response("RSS", "get_rss", feeds, None)

    def get_rss_single(self, ID):
        ID = ID[0]
        resp = self.STORE.getRSSFeed(ID)
        if resp:
            return self._response(ID, "get_rss_single", self._fmt_feed(resp), None)
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
