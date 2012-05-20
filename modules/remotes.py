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
import re
import os
import logging
import traceback
import cPickle as pickle
import random
import string
import hashlib

from modules import bencode

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
            for i,v in d.iteritems():
                self.__setattr__(i,v)
        for i,v in kwargs.iteritems():
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
        for i,v in d.iteritems():
            self.__setattr__(i, v)


class Base(object):
    def __init__(self, log, ajax, *args, **kwargs):
        self._log = log
        self._ajax = ajax
        self.settings = Settings()
        self.initialise(*args, **kwargs)
        for val in ["name", "base_url"]:
            if not hasattr(self.settings, val) or self.settings[val] is None:
                raise UndefinedError("%s is not defined" % val)

    def initialise(self, name, base_url, **kwargs):
        """Function for overriding in a subclass

        Note: 'settings' attributes `name` and  `base_url` *must* be set in this function
        
        `settings` is both a dictionary and a class (see remotes.Settings class)
        Probably appropriate to set settings.authkey and settings.passkey here (if applicable)

        If you need cookies for downloading torrents, then you should acquire / set them in this
        function and define how they are used in the fetch method
        """
        self.settings.name = None
        self.settings.long_name = None
        self.settings.base_url = None
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
                filename = self.getFilename(req.info()) or "%s.torrent" % torrentid
                filecontent = req.read()
                return (filename, filecontent)

           
            Supported methods: GET, POST
           """
        return (False, False)

    def process(self, filename, filecontent):
        """Final processing for a remote fetch

            Steps involved in processing:
            1.  Verifies that 'filecontent' is a valid bencoded file
            2.  Check that the path 'torrents/<filename>' doesn't exist
            3.  Write file to path
            4.  Tells rtorrent to load the file

            Errors / Resolution:
            1.  exit
            2.  renames file by prepending a random string ==> continue
        """
        try:
            bencode.bdecode(filecontent)
        except bencode.BTL.BTFailure:
            self._log.error("Error in remote handler '%s': not a valid bencoded string", self.settings.name)
            logging.error("Error in remote handler '%s'\n%s", self.settings.name, traceback.format_exc())
            return

        target_p = os.path.join("torrents", filename)
        if os.path.exists(target_p):
            #rename
            prepend = "".join(random.choice(string.letters) for x in range(10))
            filename = "%s-%s" % (prepend, filename)
        open("torrents/%s" % (filename), "wb").write(filecontent)
        self._ajax.load_from_remote(filename, self.settings.name, start=False)

            
            

    def getFilename(self, info):
        """Parses a urllib2 response info dict for a filename
        
        It acquires this from the Content-Disposition header
        If no filename can be obtained, it returns None
        """
        if info.has_key("Content-Disposition"):
            disp = info["Content-Disposition"]
        else:
            return None
        #parse out the filename
        match = re.search("filename=\"(.*?)\"", disp)
        if match:
            return os.path.basename(match.group(1))
        else:
            return None


    def GET(self, url, params):
        """Performs a GET request on 'url' encoding 'params'

            'url' can optionally be a urllib2.Request object 
            (e.g. if cookies are an issue)

            Returns a urllib2 file-like object"""
        req_url = "%s?%s" % (url, urllib.urlencode(params))
        print("req_url: %s" % req_url)
        return urllib2.urlopen(req_url)

    def POST(self, url, params):
        """Performs a POST request on 'url', encoding 'params'

            'url' can optionally be a urllib2.Request object 
            (e.g. if cookies are an issue)

            Returns a urllib2 file-like object"""
        return urllib2.urlopen(req_url, urllib.urlencode(params))

class RemoteStorage(object):
    """Class for storing remote 'source' settings
    
        There are no plans to make this secure
        (if it is even possible)
    """

    def __init__(self):
        try:
            self.STORE = pickle.load(open(".remotes.pickle"))
        except:
            self.STORE = {}

    def addRemote(self, name, base_url, **kwargs):
        """Add a 'source'

            Requires arguments `name` and `base_url`
            Any other arguments must be passed as keywords
        """

        randomid = hashlib.sha256(os.urandom(30))
        r = Settings(name=name, base_url=base_url, remoteid=randomid, **kwargs)
        self.STORE[randomid] = r 
        self._flush()
        return randomid

    def getRemoteByName(self, name):
        """Returns entries that have attribute name `name`

            Returns a list or None
        """
        ret = []
        for remoteid, val in self.STORE:
            if val.has_attr("name"):
                ret.append(val)
        return ret or None

    def getRemoteById(self, remoteid):
        """Returns an entry with id `remoteid`

            Returns a Settings instance, or None
        """
        if remoteid in self.STORE:
            return self.STORE[remoteid]

    def removeRemote(self, remoteid):
        """Deletes an entry with id `remoteid`

            Returns True if successful, or None
        """
        if remoteid in self.STORE:
            del self.STORE[remoteid]
            self._flush()
            return True
        
    def _flush(self):
        pickle.dump(self.STORE, open(".remotes.pickle","w"))

