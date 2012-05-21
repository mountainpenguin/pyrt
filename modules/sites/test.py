#!/usr/bin/env python

from modules import remotes
import urlparse

# DESCRIPTION should always be set
DESCRIPTION = "Example Handler"

# REQUIRED_KEYS should always be set
REQUIRED_KEYS = ["authkey","torrent_pass"]

# 'source' classes should always be named 'Main'
class Main(remotes.Base):
    def initialise(self, *args, **kwargs):
        self.settings.name = "example"
        self.settings.long_name = "Example Handler"
        self.settings.base_url = "http://example.tld"

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
