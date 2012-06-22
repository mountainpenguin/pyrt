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
import urlparse
import re

# DESCRIPTION should always be set
DESCRIPTION = "Example Handler"

# REQUIRED_KEYS should always be set
REQUIRED_KEYS = [
    ("nick", "IRC bot nick"),
]

METHODS = ["IRC"]

IRC_NETWORK = "irc.bytesized-hosting.com"
IRC_PORT = 6667
IRC_CHANNEL = "#pyrt-dev"

IRC_MATCH = re.compile("pyrtBot: (.*?)\!", re.I)

#IRC_COMMANDS = []

# 'source' classes should always be named 'Main'
class Main(remotes.Base):
    def initialise(self, *args, **kwargs):
        self.settings.name = "EXAMPLE" #name must always be the capitalised filename of this file
        self.settings.long_name = "Example Handler"
        self.settings.base_url = "http://example.tld"

    def fetch(self, torrentid):
        return None, None
        #url = urlparse.urljoin(self.settings.base_url, "torrents.php")
        #params = {
        #    "action" : "download",
        #    "id" : torrentid,
        #    "authkey" : self.settings.authkey,
        #    "torrent_pass" : self.settings.torrent_pass,
        #}
        #req = self.GET(url, params)
        #filename = self.getFilename(req.info()) or "%s.torrent" % torrentid
        #filecontent = req.read()
        #return (filename, filecontent)
