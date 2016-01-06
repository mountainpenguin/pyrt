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
import urllib
import urllib2
import requests
import re
import os
import logging
import traceback
import cPickle as pickle
import random
import string
import hashlib
import imp
import urlparse

from modules import bencode
from modules import feedparser


def searchSites():
    import modules.sites

    def _filter(name):
        if name[-3:] != ".py":
            return False
        elif name[0] == "_":
            return False
        else:
            return True
    files = filter(_filter, os.listdir("modules/sites/"))
    srcs = []
    for f in files:
        try:
            d = imp.find_module(f.split(".py")[0], ["modules/sites"])
            c = imp.load_module("modules.sites.%s" % f.split(".py")[0], d[0], d[1], d[2])
            srcs.append((f.split(".py")[0], c.DESCRIPTION, c.REQUIRED_KEYS, c.METHODS))
        except:
            logging.error(traceback.format_exc())
            pass
    return srcs


def getSiteMod(name):
    import modules.sites
    d = imp.find_module(name.lower(), ["modules/sites"])
    if d:
        c = imp.load_module("modules.sites.%s" % name.lower(), d[0], d[1], d[2])
        return c


class UndefinedError(Exception):
    def __init__(self, value):
        self.param = value

    def __str__(self):
        return repr(self.param)

    def __repr__(self):
        return "UndefinedError: %s" % self.param


class BencodeError(Exception):
    def __init__(self, value):
        self.param = value

    def __str__(self):
        return repr(self.param)

    def __repr__(self):
        return "BencodeError: %s" % self.param


class RSSFeed(dict):
    def __init__(self, rand_id, url, ttl, alias, lasthash, enabled=False, filters=[]):
        """url = string
            ttl = float: refresh rate (in minutes)
        """
        self.ID = rand_id
        self.url = url
        self.ttl = ttl
        self.alias = alias
        self.enabled = enabled
        self.filters = filters
        self.updated = 0
        self.lasthash = lasthash


class Settings(dict):
    """ Semi-implemented recursive 'dictionary object'

        Supports attribute lookups in a javascript object-esque manner
        NOTE that all dictionary keys must be strings

        Both setting attributes, and setting dictionary key methods are equivalent and interchangeable
        Example:
            >>> obj = Settings( {"testval" : "val"} ) # specifying an inital dictionary is optional
            >>> obj.testval
            'val'
            >>> obj["testval"]
            'val'
            >>> obj.name = "what.cd"
            >>> obj["name"]
            what.cd
            >>> obj["base_url"] = "http://what.cd"
            >>> obj.base_url
            http://what.cd

        Limited recursion of dictionary objects is supported
        this *only* works if the update method is used (Ex. 1),
        or via attribute assignment (Ex. 2)
        See known bugs below
        Example 1:
            >>> d = {
                    "this" : {
                        "is" : {
                            "a" : {
                                "very" : ["recursive", "object"]
                            }
                        }
                    }
                }
            >>> obj.update(d)
            >>> obj.this["is"].a.very
            ['recursive', 'object']

        Example 2:
            >>> obj.test = d
            >>> obj.test.this["is"].a.very
            ['recursive', 'object']

        Note that if you, for example, specify a list value that contains dictionaries
        these will not be evaluated
        Example:
            >>> d = { "level1" : [ { "d" :  1 }, { "d" : 2 } ] }
            >>> obj.test = d
            >>> obj.test.level1
            [{'dict':1},{'dict':2}]
            >>> obj.test.level1[0]["d"]
            1
            >>> obj.test.level1[0].d
            Traceback (most recent call last):
              File "<stdin>", line 1, in <module>
            AttributeError: 'dict' object has no attribute 'd'

        Known bugs:
        1.  Cannot set dictionaries to be recursive if key assignment is used
                >>> obj["a"] = {"b":"c"}
                >>> obj.a.b
                (...)
                AttributeError: 'dict' object has no attribute 'b'
                >>> obj.a = {"b":"c"}
                >>> obj.a.b
                'c'

            Workaround is to pre-wrap the inserted dictionary as a Settings object
                >>> obj["a"] = Settings({"b":"c"})
                >>> obj.a.b
                'c'

       """

    def __init__(self, d=None, **kwargs):
        if d:
            for i, v in d.iteritems():
                self.__setattr__(i, v)
        for i, v in kwargs.iteritems():
            self.__setattr__(i, v)

    def __setattr__(self, item, value):
        if isinstance(value, dict):
            value = Settings(value)
        self[item] = value

    def __getattr__(self, item):
        i = self.get(item)
        if not i:
            raise AttributeError(item)
        else:
            return i

    def update(self, d):
        """Overrides inbuilt dict.update method to allow setting class attributes"""
        for i, v in d.iteritems():
            self.__setattr__(i, v)


class Base(object):
    def __init__(self, log, ajax, storage, *args, **kwargs):
        self._log = log
        self._ajax = ajax
        self._storage = storage
        self.settings = Settings()
        self.initialise(*args, **kwargs)
        for val in ["name", "base_url"]:
            if not hasattr(self.settings, val) or self.settings[val] is None:
                raise UndefinedError("%s is not defined" % val)
        result = self._fetch_keywords()
        if not result:
            raise UndefinedError("No records in RemoteStorage for this class")
        self.post_init()

    def _fetch_keywords(self):
        resp = self._storage.getRemoteByName(self.settings.name.upper())
        if not resp:
            return None
        # should only ever be one entry defined
        self.settings._required_keys = resp
        return True

    def initialise(self, name, base_url, **kwargs):
        """Function for overriding in a subclass

        Note: 'settings' attributes `name` and  `base_url` *must* be set in this function

        `settings` is both a dictionary and a class (see remotes.Settings class)
        """
        self.settings.name = None
        self.settings.long_name = None
        self.settings.base_url = None
        return

    def post_init(self):
        """Function for post initialisation - for overriding (if required)

        Keywords settings that are specified in `required_keys` have already been fetched by the
        time this function is executed.
        They are stored within self.settings._required_keys, you may wish to store them
        elsewhere.

        If you need cookies for downloading torrents, then you should acquire / set them in this
        function and define how they are used in the fetch method.
        """
        return

    def fetch(self):
        """Overridable method for fetching torrents remotely

           Should be overriden to return a tuple with two elements:
                filename
                string of the torrent file
           This will be saved and loaded accordingly with the process method

           This method should hook into GET and POST methods as required

           Example:
            (...)
            self.settings.base_url = "http://nonexistant.tld"
            self.settings.authkey = "eggs"
            self.settings.passkey = "ham"
            (...)
            def fetch(self, torrentid):
                url = urlparse.urljoin(self.settings.base_url, "torrents.php")
                params = {
                    "action" : "download",
                    "authkey" : self.settings.authkey,
                    "passkey" : self.settings.passkey,
                }
                req = self.GET(url, params)
                # check if server sent a filename to use, if not, use torrentid.torrent as filename
                filename = self.getFilename(req.headers) or "%s.torrent" % torrentid
                filecontent = req.content
                return (filename, filecontent)


            Supported methods: GET, POST
           """
        return (False, False)

    def _getTorrentSize(self, bencoded):
        if "files" in bencoded["info"]:
            # multifile torrent
            length = 0
            for f in bencoded["info"]["files"]:
                length += f["length"]
        else:
            # singlefile
            length = bencoded["info"]["length"]
        return length

    def process(self, filename, filecontent, sizemin, sizemax):
        """Final processing for a remote fetch

            Steps involved in processing:
            1.  Verifies that 'filecontent' is a valid bencoded file
            2.  Checks that the size is correct
            3.  Check that the path 'torrents/<filename>' doesn't exist
            4.  Write file to path
            5.  Tells rtorrent to load the file

            Errors / Resolution:
            1.  exit
            2.  renames file by prepending a random string ==> continue
        """
        try:
            bencoded = bencode.bdecode(filecontent)
        except bencode.BTL.BTFailure:
            self._log.error("Error in remote handler '%s': not a valid bencoded string", self.settings.name)
            logging.error("Error in remote handler '%s'\n%s", self.settings.name, traceback.format_exc())
            open("test.torrent", "w").write(filecontent)
            return

        length = self._getTorrentSize(bencoded)
        if sizemax and length > sizemax:
            return
        elif sizemin and length < sizemin:
            return

        target_p = os.path.join("torrents", filename)
        if os.path.exists(target_p):
            # rename
            prepend = "".join([random.choice(string.letters) for x in range(10)])
            filename = "%s-%s" % (prepend, filename)
        open("torrents/%s" % (filename), "wb").write(filecontent)
        self._ajax.load_from_remote(filename, self.settings.name, start=True)

    def getFilename(self, info):
        """Parses a urllib2 response info dict for a filename

        It acquires this from the Content-Disposition header
        If no filename can be obtained, it returns None
        """
        if "Content-Disposition" in info:
            disp = info["Content-Disposition"]
        else:
            return None
        # parse out the filename
        match = re.search("filename=\"(.*?)\"", disp)
        if match:
            return os.path.basename(match.group(1))
        else:
            return None

    def GET(self, url, params=None):
        """Performs a GET request on 'url' encoding 'params'

            'url' can optionally be a urllib2.Request object
            (e.g. if cookies are an issue)

            Returns a urllib2 filem-like object"""
        if params:
            req_url = "%s?%s" % (url, urllib.urlencode(params))
        else:
            req_url = url
        return requests.get(req_url)
        # return urllib2.urlopen(req_url)

    def POST(self, url, params):
        """Performs a POST request on 'url', encoding 'params'

            'url' can optionally be a urllib2.Request object
            (e.g. if cookies are an issue)

            Returns a urllib2 file-like object"""
        return requests.post(url, params)
        # return urllib2.urlopen(url, urllib.urlencode(params))


class Filter(object):
    def __init__(self, positive, negative, sizelim):
        self.positive = positive
        self.negative = negative
        self.sizelim = sizelim
        self.lower = self.sizelim[0]
        self.upper = self.sizelim[1]


class RemoteStorage(object):
    """Class for storing remote 'source' settings

        There are no plans to make this secure
        (if it is even possible)
    """

    def _randomID(self, length=10):
        return "".join([random.choice(string.letters + string.digits) for x in range(length)])

    def __init__(self, log):
        self.LOG = log
        try:
            self.STORE = pickle.load(open(".remotes.pickle"))
        except:
            self.STORE = {}
        self.BOTS = {}
        self.PROCS = {}
        try:
            self.RSS = pickle.load(open(".rss.pickle"))
        except:
            self.RSS = {}
        self.SOCKETS = {
            0: [],
            1: [],
            2: [],
            3: [],
            4: [],
            5: [],
            6: [],
            7: [],
            8: [],
            9: [],
        }

    def _purgeSockets(self):
        for socknum, assigned in self.SOCKETS.iteritems():
            if assigned:
                for sockname, process in assigned:
                    if not process.is_alive():
                        # purge!
                        self.LOG.warning("Process on socket #%i (name: %s) is dead, purging", socknum, sockname)
                        logging.warning("Process on socket #%i (name: %s) is dead, purging", socknum, sockname)
                        self.releaseSocket(socknum, sockname)

    def assignSocket(self, num, name, process):
        self._purgeSockets()
        self.SOCKETS[num] += [(name, process)]

    def getFreeSocket(self):
        self._purgeSockets()
        for i in range(10):
            if not self.SOCKETS[i]:
                return i
        return random.choice(range(10))

    def assigneeSocket(self, name):
        for i in range(10):
            if name in [x[0] for x in self.SOCKETS[i]]:
                return i

    def releaseSocket(self, num, name):
        assigned = self.SOCKETS[num]
        idx = None
        count = 0
        for x in assigned:
            if name == str(x[0]):
                idx = count
                break
            count += 1
        if idx is None:
            return False
        try:
            assigned.pop(idx)
        except IndexError:
            return False
        self.SOCKETS[num] = assigned
        return True

    def addRemote(self, name, **kwargs):
        """Add a 'source'

            Requires argument `name`
            Any other arguments must be passed as keywords
        """
        # randomid = hashlib.sha256(os.urandom(30))
        r = Settings(name=name.upper(), **kwargs)
        self.STORE[name.upper()] = r
        self._flush()
        return name

    def getRemoteByName(self, name):
        """Returns entries `name`, or None"""
        if name.upper() in self.STORE:
            return self.STORE[name.upper()]

    def removeRemote(self, name):
        """Deletes an entry with id `remoteid`

            Returns True if successful, or None
        """
        if name.upper() in self.STORE:
            del self.STORE[name.upper()]
            self._flush()
            return True

    def removeFilter(self, name, index):
        if name.upper() in self.STORE:
            s = self.STORE[name.upper()]
            if "filters" in s:
                filters = s.filters
                if index < len(filters):
                    filters.pop(index)
                    self._flush()
                    return True

    def addFilter(self, name, pos, neg, sizelim):
        """Adds a regex filter to a 'source' setting

            input arguments 'pos' and 'neg' should be lists of compiled regular expressions
            These must be checked as valid regular expressions before submission
        """
        if name.upper() in self.STORE:
            s = self.STORE[name.upper()]
            try:
                filters = s.filters
            except AttributeError:
                filters = []

            filters += [Filter(pos, neg, sizelim)]
            # make sure everything is written back
            s.filters = filters
            self.STORE[name.upper()] = s
            self._flush()
            return True

    def reflowFilters(self):
        for name in self.STORE:
            try:
                f = self.STORE[name].filters
            except AttributeError:
                if "filters" in self.STORE[name]:
                    f = self.STORE[name]["filters"]
                else:
                    f = []
            # list of regexes, each is a single positive filter
            new_f = []
            for regex in f:
                if type(regex) is tuple:
                    if len(regex) == 2:
                        new_f += [Filter(regex[0], regex[1], [None, None])]
                    elif len(regex) == 3:
                        new_f += [Filter(regex[0], regex[1], regex[2])]
                elif type(regex) is Filter:
                    new_f += [regex]
                else:
                    new_f += [Filter([regex], [], [None, None])]
            self.STORE[name].filters = new_f
        self._flush()

    def deregisterBot(self, name, pid):
        if name.upper() in self.BOTS and self.BOTS[name.upper()] == int(pid):
            del self.BOTS[name.upper()]
            return True
        else:
            return False

    def registerBot(self, pid, name):
        if name.upper() in self.BOTS:
            return False

        self.BOTS[name.upper()] = int(pid)
        return int(pid)

    def isBotActive(self, name):
        if name.upper() in self.BOTS:
            return self.BOTS[name.upper()]
        else:
            return False

    def saveProc(self, name, pid, p):
        self.PROCS[pid] = (name, p)

    def delProc(self, pid):
        if pid in self.PROCS:
            p = self.PROCS[pid]
            del self.PROCS[pid]
            return p

    def getAllProcs(self):
        return self.PROCS

    def addRSSFeed(self, url, ttl, alias=None):
        try:
            ttl = float(ttl)
        except ValueError:
            raise UndefinedError("TTL must be a number")
        url_chk = urlparse.urlparse(url)
        if not url_chk.netloc:
            raise UndefinedError("URL malformed")

        # check feed is parseable
        try:
            feed_chk = feedparser.parse(url)
        except:
            raise UndefinedError("URL is not an RSS feed")
        else:
            last_item = feed_chk.entries[0]
            lasthash = hashlib.sha256(last_item.link).hexdigest()

        if not alias:
            alias = url_chk.netloc
        rand_id = self._randomID()

#        self.ID = rand_id
#        self.url = url
#        self.ttl = ttl
#        self.alias = alias
#        self.enabled = enabled
#        self.filters = filters
#        self.updated = 0
#        self.lasthash = lasthash
        newRSS = {
            "ID": rand_id, "url": url, "ttl": ttl, "alias": alias,
            "enabled": False, "filters": [], "updated": 0, "lasthash": lasthash,
        }
        # newRSS = RSSFeed(rand_id, url, ttl, alias, lasthash)
        self.RSS[rand_id] = newRSS
        self._flushRSS()

    def removeRSSFeed(self, ID):
        if ID not in self.RSS:
            return False
        else:
            del self.RSS[ID]
            self._flush()
            return True

    def enableRSSFeed(self, ID):
        if ID not in self.RSS:
            return False
        else:
            self.RSS[ID]["enabled"] = True
            self._flushRSS()
            return True

    def disableRSSFeed(self, ID):
        if ID not in self.RSS:
            return False
        else:
            self.RSS[ID]["enabled"] = False
            self._flushRSS()
            return True

    def addRSSFilter(self, ID, pos, neg, sizelim):
        if ID not in self.RSS:
            return False
        else:
            self.RSS[ID]["filters"].append(Filter(pos, neg, sizelim))
            self._flushRSS()
            return True

    def reflowRSSFilters(self):
        for ID in self.RSS:
            f = self.RSS[ID]["filters"]
            # list of regexes, each is a single positive filter
            new_f = []
            for regex in f:
                if type(regex) is tuple:
                    # count num
                    if len(regex) == 2:
                        new_f += [Filter(regex[0], regex[1], [None, None])]
                    elif len(regex) == 3:
                        new_f += [Filter(regex[0], regex[1], regex[2])]
                elif type(regex) is Filter:
                    new_f += [regex]
                else:
                    new_f += [Filter([regex], [], [None, None])]
            self.RSS[ID]["filters"] = new_f
        self._flushRSS()

    def removeRSSFilter(self, ID, index):
        if ID not in self.RSS:
            return False
        else:
            filters = self.RSS[ID]["filters"]
            if index < len(filters):
                filters.pop(index)
                self.RSS[ID]["filters"] = filters
                self._flushRSS()
                return True
            else:
                return None

    def getRSSFilters(self, ID):
        if ID not in self.RSS:
            return False
        else:
            return self.RSS[ID]["filters"]

    def _ttlhuman(self, mins):
        s = round(mins*60)
        stri = ""
        if s > 60**2:
            stri += "%ih " % (s / 60**2)
            s %= 60**2
        if s > 60:
            stri += "%im " % (s / 60)
            s %= 60
        if s > 0:
            stri += "%is" % s
        return stri

    def getRSSFeeds(self):
        return [
            {
                "id": x["ID"],
                "url": x["url"],
                "ttl_str": self._ttlhuman(x["ttl"]),
                "ttl": x["ttl"],
                "ttl_sec": x["ttl"]*60,
                "alias": x["alias"],
                "enabled": x["enabled"],
                "enabled_str": x["enabled"] and "disable" or "enable",
                "enabled_image": x["enabled"] and "images/red-x.png" or "images/submit.png",
                "filters": x["filters"],
                "lasthash": x["lasthash"],
                "updated": x["updated"],
            } for x in self.RSS.values()
        ]

    def getRSSFeed(self, ID):
        if ID in self.RSS:
            rss = self.RSS[ID]
            return {
                "id": rss["ID"],
                "url": rss["url"],
                "ttl_str": self._ttlhuman(rss["ttl"]),
                "ttl": rss["ttl"],
                "ttl_sec": rss["ttl"]*60,
                "alias": rss["alias"],
                "enabled": rss["enabled"],
                "enabled_str": rss["enabled"] and "disable" or "enable",
                "enabled_image": rss["enabled"] and "images/red-x.png" or "images/submit.png",
                "filters": rss["filters"],
                "lasthash": rss["lasthash"],
                "updated": rss["updated"],
            }
        else:
            return False

    def updateRSSFeed(self, ID, timestamp):
        if ID not in self.RSS:
            return False
        else:
            self.RSS[ID]["updated"] = timestamp
            self._flushRSS()
            return True

    def updateHashRSSFeed(self, ID, h):
        if ID not in self.RSS:
            return False
        else:
            self.RSS[ID]["lasthash"] = h
            return True

    def _flush(self):
        pickle.dump(self.STORE, open(".remotes.pickle", "w"))

    def _flushRSS(self):
        pickle.dump(self.RSS, open(".rss.pickle", "w"))
