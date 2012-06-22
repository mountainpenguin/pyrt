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

from modules import remotes
from modules import irc
import urlparse
import re

# DESCRIPTION should always be set
DESCRIPTION = "Pass the Popcorn"

# REQUIRED_KEYS should always be set
REQUIRED_KEYS = [
    ("username", "PTP username"), 
    ("authkey", "authkey"),
    ("torrent_pass", "torrent_pass"),
    ("irckey", "irckey"),
    ("nick", "IRC bot nick"),
]

# METHODS should always be set
# options are 'IRC' ('RSS' or 'WEB' to be added in the future)
METHODS = ["IRC"]

# if IRC is listed as a method, *must* define:
# IRC_NETWORK, IRC_PORT, IRC_CHANNEL, and IRC_REGEX
IRC_NETWORK = "irc.passthepopcorn.me"
IRC_PORT = 6667
IRC_CHANNEL = "#ptp-announce"
# IRC_MATCH should be a compiled regex that will extract the torrentid of
# an announce message as the first matched group
IRC_MATCH = re.compile("http://passthepopcorn\.me/torrents\.php\?id=\d+&torrentid=(\d+)")

# if special IRC authentication is required, you can define 
# commands to send sequentially on connect here
IRC_COMMANDS = [
    "PRIVMSG Hummingbird :ENTER %(settings.username)s %(settings.irckey)s " + IRC_CHANNEL,
]

# 'source' classes should always be named 'Main'
class Main(remotes.Base):
    def initialise(self, *args, **kwargs):
        self.settings.name = "PTP"
        self.settings.long_name = "passthepopcorn"
        self.settings.base_url = "http://passthepopcorn.me"

    def post_init(self):
        # note that this implementation doesn't really need to
        # override `post_init`, can easily access authkey and torrent_pass
        # in `fetch` without reassigning
        self.settings.authkey = self.settings._required_keys.authkey
        self.settings.torrent_pass = self.settings._required_keys.torrent_pass

    def fetch(self, torrentid):
        url = urlparse.urljoin(self.settings.base_url, "torrents.php")
        params = {
            "action" : "download",
            "id" : torrentid,
            "authkey" : self.settings.authkey,
            "torrent_pass" : self.settings.torrent_pass,
        }
        req = self.GET(url, params)
        filename = self.getFilename(req.info()) or "%s.torrent" % torrentid
        filecontent = req.read()
        return (filename, filecontent)

        
