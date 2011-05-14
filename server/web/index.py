#!/usr/bin/python2.5

import cgi
import os
import sys
import rtorrent
import torrentHandler
import login

form = cgi.FieldStorage()

L = login.Login()
test = L.checkLogin(os.environ)
L.loginHTML(test)
sys.exit()

if not test and not form.getfirst("password"):
    L.loginHTML(test)
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

RT = rtorrent.rtorrent("/home/torrent/.session/rpc.socket")
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
""" % {
    "main" : ttmain,
    "started" : ttstarted,
    "stopped" : ttstopped,
    "complete" : ttcomplete,
    "incomplete" : ttincomplete,
    "hashing" : tthashing,
    "seeding" : ttseeding,
    "active" : ttactive,
}
print html.replace("<!-- BODY PLACEHOLDER -->",html_insert)

