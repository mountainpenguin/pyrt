#!/usr/bin/env python

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
IRC_MATCH = re.compile("http:\/\/what\.cd\/torrents\.php\?action=download\&id=(\d+)")
    
IRC_COMMANDS = [
    "PRIVMSG Drone :ENTER " + IRC_CHANNEL + " %(settings.username)s %(settings.irckey)s"
]

class Main(remotes.Base):
    def initialise(self, *args, **kwargs):
        self.settings.name = "What"
        self.settings.long_name = "What.CD"
        self.settings.base_url = "http://what.cd"

    def fetch(self, torrentid):
        url = urlparse.urljoin(self.settings.base_url, "torrents.php")
        params = {
            "action": "download",
            "id" : torrentid,
            "authkey" : self.settings._required_keys.authkey,
            "torrent_pass" : self.settings._required_keys.torrent_pass,
        }
        req = self.GET(url, params)
        filename = self.getFilename(req.info()) or "%s.torrent" % torrentid
        filecontent = req.read()
        return (filename, filecontent)
