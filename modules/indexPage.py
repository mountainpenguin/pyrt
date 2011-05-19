#!/usr/bin/env python

import cgi
import os
import sys
import rtorrent
import torrentHandler
import login
import system
import config

class Index:
    def __init__(self):
        pass
    def index(self, password=None, view=None, sortby=None, reverse=False):
        if not view or view not in ["main","started","stopped","complete","incomplete","hashing","seeding","active"]:
            view = "main"
        if not sortby:
            sortby = "none"

        Config = config.Config()

        RT = rtorrent.rtorrent(Config.get("rtorrent_socket"))
        handler = torrentHandler.Handler()

        torrentList = RT.getTorrentList2(view)
        html = handler.torrentHTML(torrentList, sortby, view, reverse)

        def genHTML(type, VIEW):
            if VIEW == type:
                return  '<div class="topbar-tab selected" onmouseover="select_tab(this);" onmouseout="deselect_tab(this);" onclick="navigate_tab(this);" title="%s" id="tab_%s">%s</div>' % (type, type, type.capitalize())
            else:
                return '<div class="topbar-tab" onmouseover="select_tab(this);" onmouseout="deselect_tab(this);" onclick="navigate_tab(this);" title="%s" id="tab_%s">%s</div>' % (type, type, type.capitalize())
           

        ttmain = genHTML("main", view)
        ttstarted = genHTML("started",view)
        ttstopped = genHTML("stopped",view)
        ttcomplete = genHTML("complete",view)
        ttincomplete = genHTML("incomplete",view)
        tthashing = genHTML("hashing",view)
        ttseeding = genHTML("seeding",view)
        ttactive = genHTML("active",view)

        global_up_rate = handler.humanSize(RT.getGlobalUpRate())
        global_down_rate = handler.humanSize(RT.getGlobalDownRate())
        global_up_total = handler.humanSize(RT.getGlobalUpBytes())
        global_down_total = handler.humanSize(RT.getGlobalDownBytes())

        diskused, disktotal = system.hdd()
        memused, memtotal = system.mem()
        load1, load5, load15 = os.getloadavg()
        uptime = handler.humanTimeDiff(system.uptime())

        html_insert = """
              <div id="header">
                <div id="topbar">
                    %(main)s
                    %(started)s
                    %(stopped)s
                    %(complete)s
                    %(incomplete)s
                    %(hashing)s
                    %(seeding)s
                    %(active)s
                  </div>
                </div>
                <div id="main_body">
                  <div id="wrapper">
                    <div id="add_torrent">
                        <img title="Add a Torrent" alt="Add Torrent" src="/images/add.png" id="add_img" onclick="show_add_dialogue(this.parentNode);">
                    </div>
                    <div id="global_stats">
                        <h2>Global Stats</h2>
                        <div class="column-1">Upload Rate:</div><div class="column-2">%(uprate)s/s</div>
                        <div class="column-3">Total Up:</div><div class="column-4">%(uptot)s</div>
                        <div class="column-5">Disk Usage:</div><div class="column-6">%(diskused)s / %(disktotal)s</div>
                        
                        <div class="column-1">Download Rate:</div><div class="column-2">%(downrate)s/s</div>
                        <div class="column-3">Total Down:</div><div class="column-4">%(downtot)s</div>
                        <div class="column-5">Mem Usage:</div><div class="column-6">%(memused)s / %(memtotal)s</div>
                        
                        <div class="column-1">Load Average:</div>
                        <div class="column-2">
                            <span title="Last minute">%(load1)s</span>,
                            <span title="Last 5 minutes">%(load5)s</span>,
                            <span title="Last 15 minutes">%(load15)s</span>
                        </div>
                        <div class="column-3">Uptime:</div><div class="column-4">%(uptime)s</div>
                        <div class="column-5">CPU Usage:</div><div class="column-6">%(cpuusage)s%%</div>
                    </div>
        """ % {
            "main" : ttmain,
            "started" : ttstarted,
            "stopped" : ttstopped,
            "complete" : ttcomplete,
            "incomplete" : ttincomplete,
            "hashing" : tthashing,
            "seeding" : ttseeding,
            "active" : ttactive,
            "uprate" : global_up_rate,
            "downrate" : global_down_rate,
            "uptot" : global_up_total,
            "downtot" : global_down_total,
            "diskused" : handler.humanSize(diskused),
            "disktotal" : handler.humanSize(disktotal),
            "memused" : handler.humanSize(memused),
            "memtotal" : handler.humanSize(memtotal),
            "load1" : "%.02f" % load1,
            "load5" : "%.02f" % load5,
            "load15" : "%.02f" % load15,
            "cpuusage" : "None",
            "uptime" : uptime,
        }
        return html.replace("<!-- BODY PLACEHOLDER -->",html_insert).replace("</body>","</div></div>\n\t</body>")

