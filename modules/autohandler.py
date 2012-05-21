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

class AutoHandler(object):
    def __init__(self, login, log, remoteStorage):
        self.LOGIN = login
        self.LOG = log
        self.STORE = remoteStorage
        self.METHODS = {
            "get_sources" : self.get_sources,
            "set_source" : self.set_source,
            "start_bot" : self.start_bot,
        }

    def _fmt_source(self, name, desc, status):
        fmt = {
            "name" : name,
            "desc" : desc,
            "status" : status,
        }
        row_templ = "<tr class='remote_row' id='remote_name_%(name)s'><td class='name'>%(name)s</td><td class='desc'>%(desc)s</td><td class='status status-%(status)s'>%(status)s</td></tr>"
        return row_templ % fmt

    def _fmt_keys(self, name, keys):
        input_templ = "<label for='%(key)s'>%(key)s:</label><input type='text' name='%(key)s' placeholder='%(key)s'>"
        fmt = {
            "name" : name,
            "form" : "".join([ input_templ % { "key": x } for x in keys])
        }
        row_templ = """
            <tr class='is_hidden remote_setting' id='remote_settings_%(name)s'>
                <td colspan=10>
                    <!-- 
                    <h4>Controls</h4>
                        <div class="controls">
                            <img title="Start" src="/images/start.png" class="control_image">
                            <img title="Stop" src="/images/stop.png" class="control_image">
                        </div>
                    -->
                    <h4>Settings</h4>
                    <div class="settings">
                            %(form)s
                        <button type="submit" class="submit_button" id="submit_%(name)s">
                            <img src="/images/submit.png" width=20 height=20>
                            <span>Submit</span>
                        </button>
                    </div>
                </td>
            </tr>
        """
        return row_templ % fmt
            

    def start_bot(self, name):
        auth = self.LOGIN.getRPCAuth() 
        ircobj = irc.Irc(self.LOG, websocketURI=".sockets/rpc.interface", auth=auth)
        ircobj.start()

    def get_sources(self):
        sources = remotes.searchSites() 
        logging.info("Found sites: %r" % sources)
        sites = []
        if sources:
            for name, desc, req in sources:
                sites.append({
                    "row" : self._fmt_source(name, desc, "off"),
                    "requirements" : req,
                    "req_row" : self._fmt_keys(name, req),
                })
        resp = {
            "request" : "get_sources",
            "error" : None,
            "response" : sites,
        }
        return json.dumps(resp)
                
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
        resp = {
            "request" : "set_source",
            "error" : None,
            "response" : "OK",
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
            
