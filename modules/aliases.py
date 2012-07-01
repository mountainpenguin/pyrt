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

import os
import glob
import cPickle as pickle
from modules import rtorrent

class AliasError(Exception):
    def __init__(self, value):
        self.param = value
    def __str__(self):
        return repr(self.param)
    def __repr__(self):
        return "AliasError: %s" % self.param
    
class AliasGroup(object):
    def __init__(self, alias, favicon, members):
        self.alias = alias
        if len(members) > 0:
            if type(members[0]) is list:
                self.urls = members
            elif type(members[0]) is rtorrent.TrackerSimple:
                self.urls = [x.url for x in members]
            elif type(members[0]) is rtorrent.Tracker:
                self.urls = [x.root_url for x in members]
            else:
                self.urls = []
        else:
            self.urls = []
        self.members = members
        self.favicon = favicon
    
class AliasStore(object):
    """Class for storing tracker aliases / favicons
        Same instance should be shared between statsPage, optionsPage, and ajaxPage
    """
    def __init__(self, log, rt):
        if os.path.exists(".aliases.pickle"):
            self.STORE = pickle.load(open(".aliases.pickle"))
        else:
            self.STORE = self._init()
            self._flush()
            
        self.REVERSE_LOOKUP = {}
        for alias, alias_obj in self.STORE:
            for alias_url in alias_obj.urls:
                self.REVERSE_LOOKUP[alias_url] = alias
            
        self.LOG = log
        self.RT = rt
        
    # structure will be:
    #    alias: AliasGroup
    #   AliasGroup:
    #       .alias      = alias
    #       .favicon    = group favicon
    #       .urls       = list of group URLs
    #       .members    = list of rtorrent.TrackerSimple objects
    
    def getAlias(self, alias):
        """Returns the alias group for a specified alias"""
        if alias in self.STORE:
            return self.STORE[alias]
        else:
            raise AliasError("No such alias")
    
    def getAliasGroup(self, url):
        """Returns the alias group for a specified tracker URL"""
        if url in self.REVERSE_LOOKUP:
            alias = self.REVERSE_LOOKUP[url]
            return self.STORE[alias]
        else:
            raise AliasError("No such alias")
    
    def getTrackers(self):
        currTrackers = self.RT.getCurrentTrackers()
        knownTrackers = dict([(os.path.basename(x.split(".ico")[0]), rtorrent.TrackerSimple(os.path.basename(x.split(".ico")[0]), "/favicons/%s" % os.path.basename(x))) for x in glob.glob("static/favicons/*.ico")])
        #merge dictionaries
        for t_url, t in currTrackers:
            if t_url not in knownTrackers:
                knownTrackers[t_url] = t
        return knownTrackers
    
    def _init(self):
        """Initialises the database for the first time, should *only* be run if pickle file doesn't exist"""
        knownTrackers = self.getTrackers()
        aliases = {}
        for t_url, t_obj in knownTrackers:
            aliases[t_url] = AliasGroup(t_url, t_obj.favicon, [t_obj])
        return aliases
            
    def _flush(self):
        pickle.dump(self.STORE, open(".aliases.pickle","w"))