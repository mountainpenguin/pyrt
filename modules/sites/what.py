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
import re
import urlparse

DESCRIPTION = "What.CD"
REQUIRED_KEYS = [
    ("username", "what.cd username"),
    ("authkey", "authkey"),
    ("torrent_pass", "torrent_pass"),
    ("irckey", "irckey"),
    ("nick", "IRC bot nick")
]
METHODS = ["IRC"]
IRC_NETWORK = "irc.what-network.net"
IRC_PORT = 6667
IRC_CHANNEL = "#what.cd-announce"
IRC_MATCH = re.compile("https:\/\/what\.cd\/torrents\.php\?action=download\&id=(\d+)")

IRC_COMMANDS = [
    "PRIVMSG Drone :ENTER " + IRC_CHANNEL + " %(settings.username)s %(settings.irckey)s"
]

class Main(remotes.Base):
    def initialise(self, *args, **kwargs):
        self.settings.name = "What"
        self.settings.long_name = "What.CD"
        self.settings.base_url = "http://what.cd"

    def fetch(self, torrentdata):
        url = urlparse.urljoin(self.settings.base_url, "torrents.php")
        params = {
            "action": "download",
            "id" : torrentdata[0],
            "authkey" : self.settings._required_keys.authkey,
            "torrent_pass" : self.settings._required_keys.torrent_pass,
        }
        req = self.GET(url, params)
        filename = self.getFilename(req.headers) or "%s.torrent" % torrentdata[0]
        filecontent = req.content
        return (filename, filecontent)
