#!/usr/bin/env python

from __future__ import print_function
from modules import config
from modules import rtorrent
from modules import torrentHandler
from modules import system
import os
import json

class Index(object):
    def __init__(self, conf=config.Config(), RT=None):
        self.Config = conf
        if not RT:
            self.RT = rtorrent.rtorrent(self.Config.get("rtorrent_socket"))
        else:
            self.RT = RT
        self.handler = torrentHandler.Handler()

    def handle_request(self, request):
        if request == "global":
            uprate = self.RT.getGlobalUpRate()
            downrate = self.RT.getGlobalDownRate()
            loadavg = os.getloadavg()[0]
            memusage = system.mem()
            memperc = int((float(memusage[0]) / memusage[1])*100)
            return json.dumps({
                "type" : "global",
                "uprate" : uprate,
                "downrate" : downrate,
                "loadavg" : loadavg,
                "uprate_str" : self.handler.humanSize(uprate),
                "downrate_str" : self.handler.humanSize(downrate),
                "memusage" : memperc,
            })
        elif request == "trackers":
            #calculate up/down totals for each torrent
            #sort according to tracker
            #determine percentage of total up / down for each tracker
            torrentList = self.RT.getTorrentStats(view="main")
            tDict = {}
            upTotal = 0
            downTotal = 0
            ratioTotal = 0
            for t in torrentList:
                tracker_url = t.trackers[0].root_url
                if tracker_url in tDict:
                    tDict[tracker_url]["up_total"] += t.up_total
                    tDict[tracker_url]["down_total"] += t.down_total
                else:
                    tDict[tracker_url] = {}
                    tDict[tracker_url]["favicon"] = t.trackers[0].favicon_url
                    tDict[tracker_url]["up_total"] = t.up_total
                    tDict[tracker_url]["down_total"] = t.down_total
                upTotal += t.up_total
                downTotal += t.down_total

            for t in tDict:
                if tDict[t]["down_total"] > 0:
                    ratio = float(tDict[t]["up_total"]) / tDict[t]["down_total"]
                    tDict[t]["ratio"] = float(tDict[t]["up_total"]) / tDict[t]["down_total"]
                    ratioTotal += ratio
                else:
                    tDict[t]["ratio"] = 0

                tDict[t]["upShare"] = float(tDict[t]["up_total"]) / upTotal
                tDict[t]["downShare"] = float(tDict[t]["down_total"]) / downTotal
            for t in tDict:
                tDict[t]["ratioShare"] = tDict[t]["ratio"] / ratioTotal
            return json.dumps({
                "type" : "trackers",
                "data" : tDict,
            })
        else:
            return "ERROR/no such method"
