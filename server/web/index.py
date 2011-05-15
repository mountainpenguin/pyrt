#!/usr/bin/python2.5

import cgi
import os
import sys
import rtorrent
import torrentHandler
import login
import system
import config

form = cgi.FieldStorage()

L = login.Login()
test = L.checkLogin(os.environ)

if not test and not form.getfirst("password"):
    L.loginHTML()
    sys.exit()
elif not test and form.getfirst("password"):
    #check password
    pwcheck = L.checkPassword(form.getfirst("password"))
    if not pwcheck:
        L.loginHTML("Incorrect password")
        sys.exit()
    else:
        L.sendCookie()

VIEW = form.getfirst("view")
if not VIEW or VIEW not in ["main","started","stopped","complete","incomplete","hashing","seeding","active"]:
    VIEW = "main"
SORTBY = form.getfirst("sortby")
if not SORTBY:
    SORTBY = "none"
REVERSED = form.getfirst("reverse")
if not REVERSED:
    REVERSED = False

Config = config.Config()

RT = rtorrent.rtorrent(Config.get("rtorrent_socket"))
handler = torrentHandler.Handler()

torrentList = RT.getTorrentList2(VIEW)
html = handler.torrentHTML(torrentList, SORTBY, REVERSED)

def genHTML(type, VIEW):
    if VIEW == type:
        return  '<div class="topbar-tab selected" onmouseover="select_tab(this);" onmouseout="deselect_tab(this);" onclick="navigate_tab(this);" title="%s" id="tab_%s">%s</div>' % (type, type, type.capitalize())
    else:
        return '<div class="topbar-tab" onmouseover="select_tab(this);" onmouseout="deselect_tab(this);" onclick="navigate_tab(this);" title="%s" id="tab_%s">%s</div>' % (type, type, type.capitalize())
   

ttmain = genHTML("main", VIEW)
ttstarted = genHTML("started",VIEW)
ttstopped = genHTML("stopped",VIEW)
ttcomplete = genHTML("complete",VIEW)
ttincomplete = genHTML("incomplete",VIEW)
tthashing = genHTML("hashing",VIEW)
ttseeding = genHTML("seeding",VIEW)
ttactive = genHTML("active",VIEW)

global_up_rate = handler.humanSize(RT.getGlobalUpRate())
global_down_rate = handler.humanSize(RT.getGlobalDownRate())
global_up_total = handler.humanSize(RT.getGlobalUpBytes())
global_down_total = handler.humanSize(RT.getGlobalDownBytes())

diskused, disktotal = system.hdd()
memused, memtotal = system.mem()
load1, load5, load15 = os.getloadavg()
uptime = handler.humanTimeDiff(system.uptime())

html_insert = """
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
        
        <div id="main_body">
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
print html.replace("<!-- BODY PLACEHOLDER -->",html_insert).replace("</body>","</div>\n\t</body>")

