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
        self.LOG = log
        self.RT = rt
        
        if os.path.exists(".aliases.pickle"):
            self.STORE = pickle.load(open(".aliases.pickle"))
        else:
            self.STORE = self._init()
            self._flush()
            
        self.REVERSE_LOOKUP = {}
        for alias, alias_obj in self.STORE.iteritems():
            for alias_url in alias_obj.urls:
                self.REVERSE_LOOKUP[alias_url] = alias
        
    # structure will be:
    #    alias: AliasGroup
    #   AliasGroup:
    #       .alias      = alias
    #       .favicon    = group favicon
    #       .urls       = list of group URLs
    #       .members    = list of rtorrent.TrackerSimple objects
    
    def addNewAlias(self, url=None, favicon=None, trackerSimple=None):
        self._update()
        if trackerSimple:
            url = trackerSimple.url
            favicon = trackerSimple.favicon
        else:
            trackerSimple = rtorrent.TrackerSimple(url, favicon)
        
        if url in self.STORE:
            raise AliasError("Alias already defined")
        else:
            self.STORE[url] = AliasGroup(url, favicon, [trackerSimple])
            self.REVERSE_LOOKUP[url] = url
            self._flush()
        
    def getAlias(self, alias):
        """Returns the alias group for a specified alias"""
        self._update()
        if alias in self.STORE:
            return self.STORE[alias]
        else:
            raise AliasError("No such alias")
    
    def getAliasGroup(self, url):
        """Returns the alias group for a specified tracker URL"""
        self._update()
        if url in self.REVERSE_LOOKUP:
            alias = self.REVERSE_LOOKUP[url]
            return self.STORE[alias]
        else:
            raise AliasError("Unknown tracker URL")
    
    def moveTracker(self, url, newalias=None):
        """Removes a tracker URL from an alias group, and creates a new group for it
        
            if newalias is defined, new group will be named such
            else newalias will be the popped out tracker url
        """
        self._update()
        if url in self.REVERSE_LOOKUP:
            alias = self.REVERSE_LOOKUP[url]
            
            #remove from old group
            group = self.STORE[alias]
            idx = group.urls.index(url)
            oldurls = group.urls
            oldurls.pop(idx)
            group.urls = oldurls
            
            oldmembers = group.members
            thismember = oldmembers.pop(idx)
            group.members = oldmembers
            #change favicon
            #remove group if empty
            if len(oldurls) == 0:
                #delete group
                del self.STORE[alias]
            else:
                newfavicon = group.members[0].favicon
                newname = group.members[0].url
                group.favicon = newfavicon
                #rename alias to first member
                self.STORE[alias] = group
            #remove url from REVERSE_LOOKUP
            del self.REVERSE_LOOKUP[url]
            
            #create new group
            if not newalias or newalias == "null":
                newalias = url
                
            if newalias in self.REVERSE_LOOKUP:
                grp = self.STORE[self.REVERSE_LOOKUP[newalias]]
                #add to group
                oldurls = grp.urls
                oldmembers = grp.members
                oldurls += [thismember.url]
                oldmembers += [thismember]
                grp.urls = oldurls
                grp.members = oldmembers
            else:
                grp = AliasGroup(newalias, thismember.favicon, [thismember])
                
            self.STORE[newalias] = grp
            
            #deal with REVERSE_LOOKUP
            self.REVERSE_LOOKUP[url] = newalias
            
            self._flush()
        else:
            raise AliasError("Unknown tracker URL")
        
    def getTrackers(self):
        currTrackers = self.RT.getCurrentTrackers()
        knownTrackers = dict([(os.path.basename(x.split(".ico")[0]), rtorrent.TrackerSimple(os.path.basename(x.split(".ico")[0]), "/favicons/%s" % os.path.basename(x))) for x in glob.glob("static/favicons/*.ico")])
        #merge dictionaries
        for t_url, t in currTrackers.iteritems():
            if t_url not in knownTrackers:
                knownTrackers[t_url] = t
        return knownTrackers
    
    def _init(self):
        """Initialises the database for the first time, should *only* be run if pickle file doesn't exist"""
        knownTrackers = self.getTrackers()
        aliases = {}
        for t_url, t_obj in knownTrackers.iteritems():
            aliases[t_url] = AliasGroup(t_url, t_obj.favicon, [t_obj])
        return aliases

    def _update(self):
        new = self.RT.flushNewAliases()
        for n in new:
            if n.url not in self.STORE:
                self.STORE[n.url] = AliasGroup(n.url, n.favicon, [n])
                self.REVERSE_LOOKUP[n.url] = n.url
                self._flush()
                
    def _flush(self):
        pickle.dump(self.STORE, open(".aliases.pickle","w"))