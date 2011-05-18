#!/usr/bin/env python

import cgi
import rtorrent
import torrentHandler
import random
import string
import os
import sys
import time
import login
import config

class Detail:
    def __init__(self):
        self.Config = config.Config()
        self.RT = rtorrent.rtorrent(self.Config.get("rtorrent_socket"))
        self.Handler = torrentHandler.Handler()
        
    def _humanSize(self, bytes):
        if bytes > 1024*1024*1024:
            return "%.02f GB" % (float(bytes) / 1024 / 1024 / 1024)
        elif bytes > 1024*1024:
            return "%.02f MB" % (float(bytes) / 1024 / 1024)
        elif bytes > 1024:
            return "%.02f KB" % (float(bytes) / 1024)
        else:
            return "%i B" % bytes

    def main(self, torrent_id=None):
        start = time.time()
        trackers = self.RT.getTrackers(torrent_id)
        seeds = 0
        leechs = 0
        for tracker in trackers:
            seeds += tracker.seeds
            leechs += tracker.leechs
        info_dict = {
            "tname" : self.RT.getNameByID(torrent_id),
            "tid" : torrent_id,
            "tcreated" : time.strftime("%02d/%02m/%Y %02H:%02M:%02S", time.localtime(self.RT.getCreationDate(torrent_id))),
            "tpath" : self.RT.getPath(torrent_id),
            "tpriority" : self.RT.getPriorityStr(torrent_id),
            "tstate" : self.RT.getStateStr(torrent_id),
            "tsize" : self.Handler.humanSize(self.RT.getSizeBytes(torrent_id)),
            "tratio" : "%.02f" % (float(self.RT.getRatio(torrent_id))/1000),
            "tuploaded" : self.Handler.humanSize(self.RT.getUploadBytes(torrent_id)),
            "tdownloaded" : self.Handler.humanSize(self.RT.getDownloadBytes(torrent_id)),
            "tdone" : "%.02f" % (100*(float(self.RT.conn.d.get_completed_bytes(torrent_id)) / self.RT.getSizeBytes(torrent_id))),
            "tuprate" : "%s/s" % self.Handler.humanSize(self.RT.getUploadSpeed(torrent_id)),
            "tdownrate" : "%s/s" % self.Handler.humanSize(self.RT.getDownloadSpeed(torrent_id)),
            "tseeds_connected" : self.RT.conn.d.get_peers_complete(torrent_id),
            "tseeds_total" : seeds,
            "tleechs_connected" : self.RT.conn.d.get_peers_accounted(torrent_id),
            "tleechs_total" : leechs,
        }
        return """
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
    <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
            <title>rTorrent - %(tname)s</title>
            <link rel="stylesheet" type="text/css" href="../css/main.css">
            <script src="../javascript/detail.js" type="text/javascript"></script>
        </head>
        <body>
            <div id="topbar">
                <div class="topbar-tab_home" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate_home();" title="Home" id="home">Home</div>
                <div class="topbar-tab selected" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" id="info" title="Info">Info</div>
                <div class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="Peers" id="peers">Peers</div>
                <div class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="File List" id="files">File List</div>
                <div class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="Trackers" id="trackers">Tracker List</div>
            </div>
            <div id="main">
                <div class="column-1">Name:</div><div class="column-2">%(tname)s</div>
                <div class="column-1">ID:</div><div class="column-2">%(tid)s</div>
                <div class="column-1">Created:</div><div class="column-2">%(tcreated)s</div>
                <div class="column-1">Path:</div><div class="column-2">%(tpath)s</div>
                <div class="column-1">Priority:</div><div class="column-2">%(tpriority)s</div>
                <div class="column-1 %(tstate)s">State:</div><div class="column-2">%(tstate)s</div>
                <br>
                <div class="down-1"><div class="column-1">Total Size:</div><div class="column-2">%(tsize)s</div></div>
                <div class="column-1">Percentage:</div><div class="column-2">%(tdone)s%%</div>
                <div class="column-1">Ratio:</div><div class="column-2">%(tratio)s</div>
                <div class="column-1">Uploaded:</div><div class="column-2">%(tuploaded)s</div>
                <div class="column-1">Downloaded:</div><div class="column-2">%(tdownloaded)s</div>
                <br>
                <div class="down-1"><div class="column-1">Up Rate:</div><div class="column-2">%(tuprate)s</div></div>
                <div class="column-1">Down Rate:</div><div class="column-2">%(tdownrate)s</div>
               
                <div class="down-1"><div class="column-1">Leechers:</div><div class="column-2">%(tleechs_connected)s (%(tleechs_total)s)</div></div>
                <div class="column-1">Seeders:</div><div class="column-2">%(tseeds_connected)s (%(tseeds_total)s)</div>
            </div>
        </body>
    </html>""" % info_dict

    def peers(self, torrent_id=None):

        peer_html = "\n"
        colours = ["blue", "green"]
        for peer in self.RT.getPeers(torrent_id):
            colour = colours.pop(0)
            colours += [colour]
            #peer.address = ".".join(peer.address.split(".")[:2]) + ".x.x"
            peer.down_rate = "%s/s" % self.Handler.humanSize(peer.down_rate)
            peer.down_total = self.Handler.humanSize(peer.down_total)
            peer.up_rate = "%s/s" % self.Handler.humanSize(peer.up_rate)
            peer.up_total = self.Handler.humanSize(peer.up_total)
            peer.peer_rate = "%s/s" % self.Handler.humanSize(peer.peer_rate)
            peer.peer_total = self.Handler.humanSize(peer.peer_total)
            peer_html += "\t\t\t\t\t<tr class='%s'>\n" % colour
            peer_html += "\t\t\t\t\t\t<td>%(address)s</td>\n" % peer.__dict__
            peer_html += "\t\t\t\t\t\t<td>%(port)s</td><td>%(client_version)s</td><td>%(completed_percent)s%%</td>\n" % peer.__dict__
            peer_html += "\t\t\t\t\t\t<td>%(down_rate)s</td><td>%(down_total)s</td>\n" % peer.__dict__
            peer_html += "\t\t\t\t\t\t<td>%(up_rate)s</td><td>%(up_total)s</td>\n" % peer.__dict__
            peer_html += "\t\t\t\t\t\t<td>%(peer_rate)s</td><td>%(peer_total)s</td>\n" % peer.__dict__
            peer_html += "\t\t\t\t\t</tr>\n\n"

        info_dict = {
            "tname" : self.RT.getNameByID(torrent_id),
            "tid" : torrent_id,
            "tcreated" : time.strftime("%02d/%02m/%Y %02H:%02M:%02S", time.localtime(self.RT.getCreationDate(torrent_id))),
            "tpath" : self.RT.getPath(torrent_id),
            "tpriority" : self.RT.getPriorityStr(torrent_id),
            "tstate" : self.RT.getStateStr(torrent_id),
            "peerhtml" : peer_html.replace("\t","    "),
        }
        return """
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
    <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
            <title>rTorrent - %(tname)s</title>
            <link rel="stylesheet" type="text/css" href="../css/main.css">
            <script src="../javascript/detail.js" type="text/javascript"></script>
        </head>
        <body>
            <div id="topbar">
                <div class="topbar-tab_home" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate_home();" title="Home" id="home">Home</div>
                <div class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" id="info" title="Info">Info</div>
                <div class="topbar-tab selected" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="Peers" id="peers">Peers</div>
                <div class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="File List" id="files">File List</div>
                <div class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="Trackers" id="trackers">Tracker List</div>
            </div>
            <div id="main">
                <div class="column-1">Name:</div><div class="column-2">%(tname)s</div>
                <div class="column-1">ID:</div><div class="column-2">%(tid)s</div>
                <div class="column-1">Created:</div><div class="column-2">%(tcreated)s</div>
                <div class="column-1">Path:</div><div class="column-2">%(tpath)s</div>
                <div class="column-1">Priority:</div><div class="column-2">%(tpriority)s</div>
                <div class="column-1 %(tstate)s">State:</div><div class="column-2">%(tstate)s</div>
                <div id="peers_table">
                    <table>
                        <tr>
                            <td class="heading">IP Address</td>
                            <td class="heading">Port</td>
                            <td class="heading">Client</td>
                            <td class="heading">Completed</td>
                            <td class="heading">Download Rate</td>
                            <td class="heading">Download Total</td>
                            <td class="heading">Upload Rate</td>
                            <td class="heading">Upload Total</td>
                            <td class="heading">Peer Rate</td>
                            <td class="heading">Peer Total</td>
                        </tr>
                        %(peerhtml)s
                    </table>
                </div>
            </div>
        </body>
    </html>""" % info_dict


    def files(self, torrent_id=None):        
        info_dict = {
            "tname" : self.RT.getNameByID(torrent_id),
            "tid" : torrent_id,
            "tcreated" : time.strftime("%02d/%02m/%Y %02H:%02M:%02S", time.localtime(self.RT.getCreationDate(torrent_id))),
            "tpath" : self.RT.getPath(torrent_id),
            "tpriority" : self.RT.getPriorityStr(torrent_id),
            "tstate" : self.RT.getStateStr(torrent_id),
            "filehtml" : self.Handler.fileTreeHTML(self.RT.getFiles(torrent_id), self.RT.getRootDir()),
        }
        return """
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
    <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
            <title>rTorrent - %(tname)s</title>
            <link rel="stylesheet" type="text/css" href="/css/main.css">
            <script src="/javascript/detail.js" type="text/javascript"></script>
            
            <link rel="stylesheet" type="text/css" href="/css/jquery.treeview.css">
            <script src="/javascript/jquery-1.6.1.min.js" type="text/javascript"></script>
            <script src="/javascript/jquery.cookie.js" type="text/javascript"></script>
            <script src="/javascript/jquery.treeview.js" type="text/javascript"></script>
            <script src="/javascript/file.js" type="text/javascript"></script>
        </head>
        <body>
            <div id="topbar">
                <div class="topbar-tab_home" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate_home();" title="Home" id="home">Home</div>
                <div class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" id="info" title="Info">Info</div>
                <div class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="Peers" id="peers">Peers</div>
                <div class="topbar-tab selected" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="File List" id="files">File List</div>
                <div class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="Trackers" id="trackers">Tracker List</div>
            </div>
            <div id="main">
                <div class="column-1">Name:</div><div class="column-2">%(tname)s</div>
                <div class="column-1">ID:</div><div class="column-2">%(tid)s</div>
                <div class="column-1">Created:</div><div class="column-2">%(tcreated)s</div>
                <div class="column-1">Path:</div><div class="column-2">%(tpath)s</div>
                <div class="column-1">Priority:</div><div class="column-2">%(tpriority)s</div>
                <div class="column-1 %(tstate)s">State:</div><div class="column-2">%(tstate)s</div>
                %(filehtml)s
            </div>
        </body>
    </html>""" % info_dict

    def trackers(self, torrent_id=None):
        tracker_html = "\n"
        colours = ["blue", "green"]
        trackers = self.RT.getTrackers(torrent_id)
        for tracker in trackers:
            colour = colours.pop(0)
            colours += [colour]
            tracker_html += "\t\t\t\t\t<tr class='%s'>\n" % colour
            tracker_html += "\t\t\t\t\t\t<td>%(url)s</td>\n\t\t\t\t\t\t<td>%(type)s</td>\n\t\t\t\t\t\t<td>%(interval)s</td>\n\t\t\t\t\t\t<td>%(seeds)s</td>\n\t\t\t\t\t\t<td>%(leechs)s</td>\n\t\t\t\t\t\t<td>%(enabled)s</td>" % (
                {
                    "type" : {1:"HTTP",2:"UDP",3:"DHT"}[tracker.type],
                    "url" : tracker.url, #tracker.url.split("//")[0] + "//" + "***",
                    #~"url" : tracker.url.split("//")[0] + "//" + tracker.url.split("//")[1].split("/")[0] + "/***"*len(tracker.url.split("//")[1].split("/")[1:]),
                    "interval" : tracker.interval,
                    "seeds" : tracker.seeds,
                    "leechs" : tracker.leechs,
                    "enabled" : tracker.enabled,
                }
            )
            tracker_html += "\t\t\t\t\t</tr>\n"

        info_dict = {
            "tname" : self.RT.getNameByID(torrent_id),
            "tid" : torrent_id,
            "tcreated" : time.strftime("%02d/%02m/%Y %02H:%02M:%02S", time.localtime(self.RT.getCreationDate(torrent_id))),
            "tpath" : self.RT.getPath(torrent_id),
            "tpriority" : self.RT.getPriorityStr(torrent_id),
            "tstate" : self.RT.getStateStr(torrent_id),
            "trackerhtml" : tracker_html.replace("\t","    "),
        }
        return """
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
    <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
            <title>rTorrent - %(tname)s</title>
            <link rel="stylesheet" type="text/css" href="../css/main.css">
            <script src="../javascript/detail.js" type="text/javascript"></script>
        </head>
        <body>
            <div id="topbar">
                <div class="topbar-tab_home" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate_home();" title="Home" id="home">Home</div>
                <div class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" id="info" title="Info">Info</div>
                <div class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="Peers" id="peers">Peers</div>
                <div class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="File List" id="files">File List</div>
                <div class="topbar-tab selected" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="Trackers" id="trackers">Tracker List</div>

            </div>
            <div id="main">
                <div class="column-1">Name:</div><div class="column-2">%(tname)s</div>
                <div class="column-1">ID:</div><div class="column-2">%(tid)s</div>
                <div class="column-1">Created:</div><div class="column-2">%(tcreated)s</div>
                <div class="column-1">Path:</div><div class="column-2">%(tpath)s</div>
                <div class="column-1">Priority:</div><div class="column-2">%(tpriority)s</div>
                <div class="column-1 %(tstate)s">State:</div><div class="column-2">%(tstate)s</div>
                <div id="peers_table">
                    <table>
                        <tr>
                            <td class="heading">URL</td>
                            <td class="heading">Type</td>
                            <td class="heading">Announce Interval</td>
                            <td class="heading">Seeders</td>
                            <td class="heading">Leechers</td>
                            <td class="heading">Enabled</td>
                        </tr>
                        %(trackerhtml)s
                    </table>
                </div>
            </div>
        </body>
    </html>""" % info_dict

if __name__ == "__main__":

    form = cgi.FieldStorage()

    torrent_id = form.getfirst("torrent_id", None)
    view = form.getfirst("view", None)

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
            print self.Handler.HTMLredirect("/web/index.py")

    if view not in ["info", "peers", "files", "trackers"]:
        view = "info"

    if not torrent_id:
        if os.environ.get("REQUEST_METHOD") == "POST":
            try:
                torrent_id = os.environ.get("QUERY_STRING").split("torrent_id=")[1].split("&")[0]
                view = os.environ.get("QUERY_STRING").split("view=")[1].split("&")[0]
            except:
                pass

    if not torrent_id:
        print "ERROR/Not Implemented"
    elif not view or view == "info":
        main(torrent_id)
    elif view == "peers":
        peers(torrent_id)
    elif view == "files":
        files(torrent_id)
    elif view == "trackers":
        trackers(torrent_id)
