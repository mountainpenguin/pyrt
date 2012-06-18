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

import urlparse
import logging
import json
import re
import cgi
import traceback
import os
import signal


class AutoHandler(object):
    def __init__(self, login, log, remoteStorage):
        self.LOGIN = login
        self.LOG = log
        self.STORE = remoteStorage
        self.METHODS = {
            "get_sources" : self.get_sources,
            "get_source_single" : self.get_source_single,
            "set_source" : self.set_source,
            "start_bot" : self.start_bot,
            "stop_bot" : self.stop_bot,
            "get_filters" : self.get_filters,
            "add_filter" : self.add_filter,
            "remove_filter" : self.remove_filter,
        }

    def _fmt_source(self, name, desc, status):
        fmt = {
            "name" : name,
            "desc" : desc,
            "status" : status,
        }
        row_templ = "<tr class='remote_row' id='remote_name_%(name)s'><td class='name'>%(name)s</td><td class='desc'>%(desc)s</td><td class='status status-%(status)s status-%(name)s'>%(status)s</td></tr>"
        return row_templ % fmt

    def _fmt_keys(self, name, keys, filters, botcontrol):
        input_templ = "<label for='%(key)s'>%(key)s:</label><input type='text' name='%(key)s' placeholder='%(desc)s'>"
        fmt = {
            "name" : name,
            "form" : "".join([ input_templ % { "key": x[0], "desc" : x[1] } for x in keys]),
            "filters" : filters,
            "botbutton" : botcontrol,
        }
        row_templ = """
            <tr class='is_hidden remote_setting' id='remote_settings_%(name)s'>
                <td colspan=10>
                    <div class="settings">
                        <h4>Settings</h4>
                            %(form)s
                        <div class="submit_buttons">
                            <button type="submit" class="submit_button" id="submit_%(name)s">
                                <img src="/images/submit.png" width=20 height=20>
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

    def _fmt_filters(self, filters):
        filter_templ = """
            <label for='filter%(count)d'>Filter:</label><div name='filter%(count)d' class='filter'><code>%(filter)s</code></div>
        """
        fmt = {
            "filters" : "".join([ filter_templ % { "filter" : cgi.escape(x.pattern), "count": filters.index(x) + 1 } for x in filters]),
        }
        templ = """
            <div class="filters">
                <h4>Filters</h4>
                %(filters)s
                <div class="add_filter_div">
                    <label for="add_filter">
                        <button class="add_filter_button">Add Filter</button>
                    </label>
                    <input name="add_filter" id="add_filter" type="text" placeholder="Filter">
                </div>
            </div>
        """
        return templ % fmt

    def stop_bot(self, name):
        botpid = self.STORE.isBotActive(name)
        if botpid:
            os.kill(botpid, signal.SIGTERM)
            #deregister bot
            self.STORE.deregisterBot(name, botpid)
            return json.dumps({
                "request" : "stop_bot",
                "error" : None,
                "response" : name,
            })
        else:
            return json.dumps({
                "request" : "stop_bot",
                "error": "Bot not active",
                "response" : None,
            })

    def start_bot(self, name):
        auth = self.LOGIN.getRPCAuth() 
        try:
           ircobj = irc.Irc(name, self.LOG, self.STORE, websocketURI=".sockets/rpc.interface", auth=auth)
           ircobj.start()
        except:
            tb = traceback.format_exc()
            self.LOG.error("AUTO: error starting IRC bot for handler '%s' - %s", name, tb.strip().split("\n")[-1])
            logging.error(tb)
            return "ERROR/Faulty configuration for handler"
        return json.dumps({
            "request" : "start_bot",
            "error" : None,
            "response" : name,
        })

    def get_source_single(self, select):
        sources = remotes.searchSites()
        if sources:
            for name, desc, req in sources:
                if name.upper() != select.upper():
                    continue
                #determine if bot is running
                status = self._get_status(name)
                if status == "off":
                    statusimage = "on.png"
                    startstopmsg = "Start IRC"
                    startstop = "start"
                else:
                    statusimage = "off.png"
                    startstopmsg = "Stop IRC"
                    startstop = "stop"

                if self.STORE.getRemoteByName(name):
                    filters = self.get_filters(name, internal=True)
                    filters = self._fmt_filters(filters)
                    botcontrol = """
                        <button class="bot_button" id="%(startstop)s_%(name)s">
                            <img src="/images/%(statusimage)s" width=20 height=20>
                            <span>%(startstopmsg)s</span>
                        </button>
                    """ % { "statusimage" : statusimage, "startstop" : startstop, "startstopmsg" : startstopmsg, "name" : name }
                else:
                    filters = ""
                    botcontrol = ""

                return json.dumps({
                    "request" : "get_source_single",
                    "error" : None,
                    "response" : {
                        "row" : self._fmt_source(name, desc, status),
                        "requirements" : req,
                        "req_row" : self._fmt_keys(name, req, filters, botcontrol),
                    }
                })

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
            for name, desc, req in sources:
                #determine if bot is running
                status = self._get_status(name)
                if status == "off":
                    statusimage = "on.png"
                    startstopmsg = "Start IRC"
                    startstop = "start"

                else:
                    statusimage = "off.png"
                    startstopmsg = "Stop IRC"
                    startstop = "stop"

                #fetch filters
                if self.STORE.getRemoteByName(name):
                    filters = self.get_filters(name, internal=True)
                    filters = self._fmt_filters(filters)
                    botcontrol = """
                        <button class="bot_button" id="%(startstop)s_%(name)s">
                            <img src="/images/%(statusimage)s" width=20 height=20>
                            <span>%(startstopmsg)s</span>
                        </button>
                    """ % { "statusimage" : statusimage, "startstop" : startstop, "startstopmsg" : startstopmsg, "name" : name }
                else:
                    filters = ""
                    botcontrol = ""

                sites.append({
                    "row" : self._fmt_source(name, desc, status),
                    "requirements" : req,
                    "req_row" : self._fmt_keys(name, req, filters, botcontrol),
                })
        resp = {
            "request" : "get_sources",
            "error" : None,
            "response" : sites,
        }
        return json.dumps(resp)
                
    def get_filters(self, name, internal=False):
        s = self.STORE.getRemoteByName(name)
        if not s and not internal:
            return "ERROR/no store for name '%s'" % name
        elif not s and internal:
            return []

        try:
            f = s.filters
        except AttributeError:
            f = []

        if not internal:
            return json.dumps({
                "request" : "get_filters",
                "error" : None,
                "response" : [x.pattern for x in f],
            })
        else:
            return f 

    def add_filter(self, name, restring):
        name = name[0]
        restring = restring[0]
        s = self.STORE.getRemoteByName(name)
        if not s:
            return "ERROR/no store for name '%s'" % name

        #attempt to compile the re string
        try:
            regex = re.compile(restring)
        except:
            return "ERROR/invalid regex"

        if self.STORE.addFilter(name, regex):
            #send sigurg
            return json.dumps({
                "request" : "add_filter",
                "error" : None,
                "response" : name,
            })
        else:
            return "ERROR/Unknown"
        
    def remove_filter(self, name, index):
        name = name[0]
        try:
            index = int(index[0])
        except ValueError:
            return "ERROR/Not an integer"

        r = self.STORE.removeFilter(name, index)
        if r:
            return json.dumps({
                "request" : "remove_filter",
                "error" : None,
                "response" : name,
            })
        else:
            return "ERROR/No such filter index"

    def set_source(self, **kwargs):
        settings = {
        }
        for k, v in kwargs.iteritems():
            if k == "auth":
                pass
            else:
                settings[k] = v[0]
        if "name" not in settings:
            return "ERROR/name must be set"

        name = self.STORE.addRemote(**settings)
        if name:
            self.LOG.info("New remote added: '%s'" % name)
            resp = {
                "request" : "set_source",
                "error" : None,
                "response" : "OK",
            }
            return json.dumps(resp)
        else:
            self.LOG.error("Error in adding remote: '%s'" % name)
            resp = {
                "request" : "set_source",
                "error" : True,
                "response" : "ERROR",
            }
            return json.dumps(resp)

    def handle_message(self, message):
        urlparams =  urlparse.parse_qs(message)
        request = urlparams.get("request") and urlparams.get("request")[0] or None
        arguments = urlparams.get("arguments") or []
        #parse for keywords (not 'request', and not 'arguments')
        def _miniCheck(arg):
            if arg[0] == "request" or arg[0] == "arguments":
                return False
            else:
                return True

        keywords = dict( filter( _miniCheck, urlparams.items()))
        if not request:
            logging.info("autoSocket: no request specified")
            return
        elif request not in self.METHODS:
            logging.info("autoSocket: request '%r' is not supported", request)
            return "ERROR/request '%r' is not supported" % request
        else:
            return self.METHODS[request](*arguments, **keywords)
            
