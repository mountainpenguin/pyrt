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

        self.HTML = """
            <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
            <html>
                <head>
                    <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
                    <title>rTorrent - %(tname)s</title>
                    <link rel="stylesheet" type="text/css" href="/css/%(css)s.css">
                    <link rel="stylesheet" type="text/css" href="/css/smoothness/jquery-ui-1.8.13.custom.css">                    
                    %(head_add)s
                    <link rel="stylesheet" type="text/css" href="/css/jquery.treeview.css">
                    <script src="/javascript/jquery-1.6.1.min.js" type="text/javascript"></script>
                    <script src="/javascript/jquery-ui-1.8.13.custom.min.js" type="text/javascript"></script>        
                    <script src="/javascript/jquery.cookie.js" type="text/javascript"></script>
                    <script src="/javascript/jquery.treeview.js" type="text/javascript"></script>
                    <script src="/javascript/file.js" type="text/javascript"></script>
                    <script src="/javascript/%(js)s.js" type="text/javascript"></script>  
                </head>
                <body>
                  <div id="accordion">
                    <h3><a href="#">Torrent info</a></h3>
                    <div>
                        <p>Name: %(tname)s</p>
                        <p>ID: %(tid)s</p>
                        <p>Created: %(tcreated)s</p>
                        <p>Path: %(tpath)s</p>
                        <p>Priority: %(tpriority)s</p>
                        <p class="%(tstate)s">State: %(tstate)s</p>
                    </div>
                    <h3><a href="#">Peers</a></h3>                    
                    <div>
                      %(peers)s
                    </div>
                    <h3><a href="#">File list</a></h3>                    
                    <div>
                      %(filelist)s
                    </div>
                    <h3><a href="#">Tracker list</a></h3>                    
                    <div>
                      %(trackers)s
                    </div>
                  </div>

              </body>
            </html>
        """
           # <span class="topbar-tab_home" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate_home();" title="Home" id="home">Home</span>
           #  <span class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" id="info" title="Info">Info</span>
           #  <span class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="Peers" id="peers">Peers</span>
           #  <span class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="File List" id="files">File List</span>
           #  <span class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="Trackers" id="trackers">Tracker List</span>
    # tname     : torrent name
    # css       : css file name
    # js        : js file name
    # head_add  : any addition to <head> tag
    # space1    : anything in <div id="main"> (after general info)
    # space2    : anything after <div id="main">
    # space3    : anything after <div id="wrapper">
    # tname, tid, tcreated, tpath, tpriority, tstate : as expected
    
    def _getDefaults(self, torrent_id):
        return {
            "tid" : torrent_id,
            "tname" : self.RT.getNameByID(torrent_id),
            "tcreated" : time.strftime("%02d/%02m/%Y %02H:%02M:%02S", time.localtime(self.RT.getCreationDate(torrent_id))),
            "tpath" : self.RT.getPath(torrent_id),
            "tpriority" : self.RT.getPriorityStr(torrent_id),
            "tstate" : self.RT.getStateStr(torrent_id),
            "peers" :self.peers(torrent_id),
            "filelist": self.files(torrent_id),
            "trackers": self.trackers(torrent_id)
        }
    def main(self, torrent_id=None):
        start = time.time()
        trackers = self.RT.getTrackers(torrent_id)
        seeds = 0
        leechs = 0
        for tracker in trackers:
            seeds += tracker.seeds
            leechs += tracker.leechs
        info_dict = {
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
            "css" : "detail",
            "js" : "detail",
            "head_add" : "",
            "space1" : "",
            "space2" : "",
            "space3" : "",
        }
        info_dict.update(self._getDefaults(torrent_id))
        
        SPACE1_HTML = """
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
        """ % info_dict
        
        info_dict["space1"] = SPACE1_HTML
        return self.HTML % info_dict

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

        SPACE1_HTML = """
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
                        %s
                    </table>
                </div>
        """ % peer_html.replace("\t","    ")
        
        
        return SPACE1_HTML

    def files(self, torrent_id=None):
        
        SPACE1_HTML = """
                <div id="files_container">
                    %s
                </div>
                <div id="popupContact">
                    <a id="popupContactClose">x</a>
                    <h1 id="fileName">Testing Filename</h1>
                    <p id="contactArea">
                        Testing popup
                    </p>
                </div>
                <div id="backgroundPopup"></div>
        """ % self.Handler.fileTreeHTML(self.RT.getFiles(torrent_id), self.RT.getRootDir())

        
        return SPACE1_HTML

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
                    "url" : tracker.url, 
                    "interval" : tracker.interval,
                    "seeds" : tracker.seeds,
                    "leechs" : tracker.leechs,
                    "enabled" : tracker.enabled,
                }
            )
            tracker_html += "\t\t\t\t\t</tr>\n"

        SPACE1_HTML = """
                <div id="trackers_table">
                    <table>
                        <tr>
                            <td class="heading">URL</td>
                            <td class="heading">Type</td>
                            <td class="heading">Announce Interval</td>
                            <td class="heading">Seeders</td>
                            <td class="heading">Leechers</td>
                            <td class="heading">Enabled</td>
                        </tr>
                        %s
                    </table>
                </div>
        """ % tracker_html.replace("\t","    ")
        
        return SPACE1_HTML