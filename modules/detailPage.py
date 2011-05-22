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
    def __init__(self, torrent_id):
        self.Config = config.Config()
        self.RT = rtorrent.rtorrent(self.Config.get("rtorrent_socket"))
        self.Handler = torrentHandler.Handler()

        self.HTML = """
            <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
            <html>
                <head>
                    <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
                    <title>rTorrent - %(tname)s</title>
                    <link rel="stylesheet" type="text/css" href="/css/detail.css">
                    <link rel="stylesheet" type="text/css" href="/css/smoothness/jquery-ui-1.8.13.custom.css">                    
                    <link rel="stylesheet" type="text/css" href="/css/jquery.treeview.css">
                    <script src="/javascript/jquery-1.6.1.min.js" type="text/javascript"></script>
                    <script src="/javascript/jquery-ui-1.8.13.custom.min.js" type="text/javascript"></script>        
                    <script src="/javascript/jquery.cookie.js" type="text/javascript"></script>
                    <script src="/javascript/jquery.treeview.js" type="text/javascript"></script>
                    <script src="/javascript/file.js" type="text/javascript"></script>
                    <script src="/javascript/detail.js" type="text/javascript"></script>  
                </head>
                <body>
                  <div id="accordion">
                    <h3><a href="#">Torrent info</a></h3>
                    <div id="info_within">
                        <p>Name: %(tname)s</p>
                        <p>ID: %(tid)s</p>
                        <p>Created: %(tcreated)s</p>
                        <p>Path: %(tpath)s</p>
                        <p>Priority: %(tpriority)s</p>
                        <p class="%(tstate)s">State: %(tstate)s</p>
                        <p>Completion: %(tdone)s%%</p>
                        <p>Size: %(tsize)s</p>
                        <p>Ratio: %(tratio)s</p>
                        <p>Downloaded: %(tdownloaded)s</p>
                        <p>Uploaded: %(tuploaded)s</p>
                        <p>Upload Rate: %(tuprate)s</p>
                        <p>Download Rate: %(tdownrate)s</p>
                        <p>Leechers: %(tleechs_connected)s (%(tleechs_total)s)</p>
                        <p>Seeders: %(tseeds_connected)s (%(tseeds_total)s)</p>
                    </div>
                    <h3><a href="#">Peers</a></h3>
                    <div id="peers_within">
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
                                %(peer_table_rows)s
                            </table>
                        </div>
                    </div>
                    <h3><a href="#">File list</a></h3>                    
                    <div id="files_within">
                      %(filelist)s
                    </div>
                    <h3><a href="#">Tracker list</a></h3>
                    <div id="trackers_within">
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
                                %(tracker_table_rows)s
                              </table>
                            </div>
                        </div>
                   </div>
              </body>
            </html>
        """ % self._getInfo(torrent_id)
    
    def _getInfo(self, torrent_id):
        #for use by other lines
        _size = self.RT.getSizeBytes(torrent_id)
        _trackers = self.RT.getTrackers(torrent_id)
        #end 'preload'
        
        #general info
        tname = self.RT.getNameByID(torrent_id)
        tcreated = time.strftime("%02d/%02m/%Y %02H:%02M:%02S", time.localtime(self.RT.getCreationDate(torrent_id)))
        tpath = self.RT.getPath(torrent_id)
        tpriority = self.RT.getPriorityStr(torrent_id)
        tstate = self.RT.getStateStr(torrent_id)
        tsize = self.Handler.humanSize(_size)
        tratio = "%.02f" % (float(self.RT.getRatio(torrent_id))/1000)
        tuploaded = self.Handler.humanSize(self.RT.getUploadBytes(torrent_id))
        tdownloaded = self.Handler.humanSize(self.RT.getDownloadBytes(torrent_id))
        tdone = "%.02f" % (100*(float(self.RT.conn.d.get_completed_bytes(torrent_id)) / _size))
        tuprate = "%s/s" % self.Handler.humanSize(self.RT.getUploadSpeed(torrent_id))
        tdownrate = "%s/s" % self.Handler.humanSize(self.RT.getDownloadSpeed(torrent_id))
        tseeds_connected = self.RT.conn.d.get_peers_complete(torrent_id)
        tseeds_total = sum([tracker.seeds for tracker in _trackers])
        tleechs_connected = self.RT.conn.d.get_peers_accounted(torrent_id)
        tleechs_total = sum([tracker.leechs for tracker in _trackers])
        #end general info
        
        #html inserts
        files = self.Handler.fileTreeHTML(self.RT.getFiles(torrent_id), self.RT.getRootDir())
        peer_table_rows = self.peers(torrent_id)
        tracker_table_rows = self.trackers(_trackers)
        #end html inserts
        
        return {
            "tid" : torrent_id,
            "tname" : tname,
            "tcreated" : tcreated,
            "tpath" : tpath,
            "tpriority" : tpriority,
            "tstate" : tstate,
            "tsize" : tsize,
            "tratio" : tratio,
            "tuploaded" : tuploaded,
            "tdownloaded" : tdownloaded,
            "tdone" : tdone,
            "tuprate" : tuprate,
            "tdownrate" : tdownrate,
            "tseeds_connected" : tseeds_connected,
            "tseeds_total" : tseeds_total,
            "tleechs_connected" : tleechs_connected,
            "tleechs_total" : tleechs_total,
            "peer_table_rows" : peer_table_rows,
            "filelist" : files,
            "tracker_table_rows": tracker_table_rows,
        }

    def peers(self, torrent_id):
        PEER_ROW_TEMPLATE = """
                                <tr class="peer_tablerow">
                                    <td>%(address)s</td>
                                    <td>%(port)s</td>
                                    <td>%(down_rate)s</td>
                                    <td>%(down_total)s</td>
                                    <td>%(up_rate)s</td>
                                    <td>%(up_total)s</td>
                                    <td>%(peer_rate)s</td>
                                    <td>%(peer_total)s</td>
                                </tr>
        """
        PEER_HTML = ""
        for peer in self.RT.getPeers(torrent_id):
            peer_info = {
                "address" : peer.address,
                "port" : peer.port,
                "down_rate" : "%s/s" % self.Handler.humanSize(peer.down_rate),
                "down_total" : self.Handler.humanSize(peer.down_total),
                "up_rate" : "%s/s" % self.Handler.humanSize(peer.up_rate),
                "up_total" : self.Handler.humanSize(peer.up_total),
                "peer_rate" : "%s/s" % self.Handler.humanSize(peer.peer_rate),
                "peer_total" : self.Handler.humanSize(peer.peer_total)
            }
            PEER_HTML += PEER_ROW_TEMPLATE % peer_info

        return PEER_HTML

    def trackers(self, trackers):
        TRACKER_ROW_TEMPLATE = """
                                <tr class="tracker_tablerow">
                                    <td>%(url)s</td>
                                    <td>%(type)s</td>
                                    <td>%(interval)s</td>
                                    <td>%(seeds)s</td>
                                    <td>%(leechs)s</td>
                                    <td>%(enabled)s</td>
                                </tr>
        """
        TRACKER_HTML = ""
        for tracker in trackers:
            TRACKER_HTML += TRACKER_ROW_TEMPLATE % tracker.__dict__
        
        return TRACKER_HTML