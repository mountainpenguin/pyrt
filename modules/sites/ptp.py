#!/usr/bin/env python

from modules import remotes
import urlparse

class PTP(remotes.Base):
    def initialise(self, *args, **kwargs):
        self.settings.name = "PTP"
        self.settings.long_name = "passthepopcorn"
        self.settings.base_url = "http://passthepopcorn.me"
        self.settings.authkey = kwargs["authkey"]
        self.settings.torrent_pass = kwargs["torrent_pass"]

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
