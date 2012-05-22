#!/usr/bin/env python

from modules import remotes
import urlparse

# DESCRIPTION should always be set
DESCRIPTION = "Example Handler"

# REQUIRED_KEYS should always be set
REQUIRED_KEYS = [
    ("nick", "IRC bot nick"),
]

METHODS = ["IRC"]

IRC_NETWORK = "irc.mpengu.in"
IRC_PORT = 6667
IRC_CHANNEL = "#mp-dev"

# 'source' classes should always be named 'Main'
class Main(remotes.Base):
    def initialise(self, *args, **kwargs):
        self.settings.name = "example"
        self.settings.long_name = "Example Handler"
        self.settings.base_url = "http://example.tld"

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
