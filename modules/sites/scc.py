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
import os

# DESCRIPTION should always be set
DESCRIPTION = "SceneAccess"

# REQUIRED_KEYS should always be set
REQUIRED_KEYS = [
    ("nick", "IRC bot nick"),
    ("password", "NickServ password"),
    ("authkey", "authkey"),
]

METHODS = ["IRC"]

IRC_NETWORK = "irc.sceneaccess.eu"
IRC_PORT = 6667
IRC_CHANNEL = "#announce"

IRC_MATCH = re.compile("-> (.*?) \(.*?\) - \(.*?https://sceneaccess\.eu/details\.php\?id=(\d+).*?\)", re.I)

IRC_COMMANDS = [
    "PRIVMSG NickServ :IDENTIFY %(settings.password)s",
    "JOIN #announce",
]

IRC_DELAY = 5


class Main(remotes.Base):
    """ Note that the SCC bot requires a vhost as per https://sceneaccess.eu/wiki?action=article&id=31 """
    def initialise(self, *args, **kwargs):
        self.settings.name = "SCC"  # name must always be the capitalised filename of this file
        self.settings.long_name = "sceneaccess"
        self.settings.base_url = "https://sceneaccess.eu"

    def post_init(self):
        # acquire login and invite from scc
        self.settings.authkey = self.settings._required_keys.authkey

    def fetch(self, torrentdata):
        data_section = os.path.join(
            "download",
            torrentdata[1],
            self.settings.authkey,
            "{0}.torrent".format(torrentdata[0])
        )
        url = urlparse.urljoin(
            self.settings.base_url,
            data_section
        )

        req = self.GET(url)
        filename = self.getFilename(req.headers) or "%s.torrent" % torrentdata[0]
        filecontent = req.content
        return (filename, filecontent)
