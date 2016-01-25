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
from modules import misc
from modules import system
import os
import json


class Stats(object):
    def __init__(self, app):
        self.application = app
        self.Config = app._pyrtConfig
        self.RT = app._pyrtRT
        self.aliases = app._pyrtAliasStorage

    def handle_request(self, request):
        if request == "global":
            uprate = self.RT.getGlobalUpRate()
            downrate = self.RT.getGlobalDownRate()
            loadavg = os.getloadavg()[0]
            memusage = system.mem()
            memperc = int((float(memusage[0]) / memusage[1])*100)
            hdusage = system.hdd(self.Config.get("root_directory"))
            hdperc = int((float(hdusage[0]) / hdusage[1])*100)
            return json.dumps({
                "type": "global",
                "uprate": uprate,
                "downrate": downrate,
                "loadavg": loadavg,
                "uprate_str": misc.humanSize(uprate),
                "downrate_str": misc.humanSize(downrate),
                "memusage": memusage[0],
                "memmax": memusage[1],
                "memperc": memperc,
                "memusage_human": misc.humanSize(memusage[0]),
                "memmax_human": misc.humanSize(memusage[1]),
                "hdperc": hdperc,
                "hdusage": hdusage[0],
                "hdmax": hdusage[1],
                "hdusage_human": misc.humanSize(hdusage[0]),
                "hdmax_human": misc.humanSize(hdusage[1]),
            })
        elif request == "trackers":
            # calculate up/down totals for each torrent
            # sort according to tracker
            # determine percentage of total up / down for each tracker
            torrentList = self.RT.getTorrentStats(view="main")
            tDict = {}
            upTotal = 0
            downTotal = 0
            ratioTotal = 0
            for t in torrentList:
                tracker_url = t.trackers[0].root_url
                # get alias
                try:
                    alias = self.aliases.getAliasGroup(tracker_url)
                except:
                    pass
                else:
                    alias_url = alias.alias
                    if alias_url in tDict:
                        tDict[alias_url]["up_total"] += t.up_total
                        tDict[alias_url]["down_total"] += t.down_total
                    else:
                        tDict[alias_url] = {}
                        tDict[alias_url]["favicon"] = alias.favicon
                        tDict[alias_url]["up_total"] = t.up_total
                        tDict[alias_url]["down_total"] = t.down_total
                upTotal += t.up_total
                downTotal += t.down_total

            for t in tDict:
                if tDict[t]["down_total"] > 0:
                    ratio = float(tDict[t]["up_total"]) / tDict[t]["down_total"]
                    tDict[t]["ratio"] = float(tDict[t]["up_total"]) / tDict[t]["down_total"]
                    ratioTotal += ratio
                else:
                    tDict[t]["ratio"] = 0

                if upTotal > 0:
                    tDict[t]["upShare"] = float(tDict[t]["up_total"]) / upTotal
                else:
                    tDict[t]["upShare"] = 0
                if downTotal > 0:
                    tDict[t]["downShare"] = float(tDict[t]["down_total"]) / downTotal
                else:
                    tDict[t]["downShare"] = 0
            for t in tDict:
                if ratioTotal > 0:
                    tDict[t]["ratioShare"] = tDict[t]["ratio"] / ratioTotal
                else:
                    tDict[t]["ratioShare"] = 0
                tDict[t]["up_total"] = misc.humanSize(tDict[t]["up_total"])
                tDict[t]["down_total"] = misc.humanSize(tDict[t]["down_total"])
            return json.dumps({
                "type": "trackers",
                "data": tDict,
            })
        else:
            return "ERROR/no such method"
