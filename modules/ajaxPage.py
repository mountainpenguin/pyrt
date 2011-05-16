#!/usr/bin/python2.5

import cgi
import rtorrent
import simplejson as json
import time
import torrentHandler
import login
import os
import sys
import config

class Peer:
    def __init__(self, address, client_version, completed_percent, down_rate, down_total, up_rate, up_total, port):
        self.address = address
        self.client_version = client_version
        self.completed_percent = completed_percent
        self.down_rate = down_rate
        self.down_total = down_total
        self.up_rate = up_rate
        self.up_total = up_total
        self.port = port

class Torrent:
    def __init__(self, torrent_id):
        self.torrent_id = torrent_id

        self.name = RT.getNameByID(torrent_id)
        self.uploaded = Handler.humanSize(RT.getUploadBytes(torrent_id))
        self.downloaded = Handler.humanSize(RT.getDownloadBytes(torrent_id))
        self.size = Handler.humanSize(float(RT.getSizeBytes(torrent_id)))
        self.ratio = "%.02f" % (float(RT.getRatio(torrent_id))/1000)
        self.created = RT.conn.d.get_creation_date(torrent_id)
        self.trackers = []
        for x in range(100):
            try:
                self.trackers += [RT.conn.t.get_url(torrent_id, x)]
            except:
                break
        self.peers = []
        # peer_exchange_len = RT.conn.d.get_peer_exchange(torrent_id)
        # peers_accounted_len = RT.conn.d.get_peers_accounted(torrent_id)
        # peers_complete_len = RT.conn.d.get_peers_complete(torrent_id)
        peers_connected_len = RT.conn.d.get_peers_connected(torrent_id)
    
        if peers_connected_len > 0:
            #get peers
            peers_connected = []
            resp = RT.conn.p.multicall(
                                        torrent_id,
                                        " ",
                                        "p.get_address=",
                                        "p.get_client_version=",
                                        "p.get_completed_percent=",
                                        "p.get_down_rate=",
                                        "p.get_down_total=",
                                        "p.get_up_rate=",
                                        "p.get_up_total=",
                                        "p.get_port=",
                                      )
            for i in range(peers_connected_len):
                self.peers += [Peer(resp[i][0], resp[i][1], resp[i][2], resp[i][3], resp[i][4], resp[i][5], resp[i][6], resp[i][7]).__dict__]

class Ajax:
    def __init__(self):
        self.Config = config.Config()
        self.RT = rtorrent.rtorrent(self.Config.get("rtorrent_socket"))
        self.Handler = torrentHandler.Handler()
        
    def get_torrent_info(self, torrent_id):
        c = time.localtime(self.RT.getCreationDate(torrent_id))
        created = time.strftime("%d/%m/%Y %H:%M:%S", c)
        jsonObject = {
            "name" : self.RT.getNameById(torrent_id),
            "uploaded" : self.Handler.humanSize(self.RT.getUploadBytes(torrent_id)),
            "downloaded" : self.Handler.humanSize(self.RT.getDownloadBytes(torrent_id)),
            "peers" : self.RT.getPeers(torrent_id),
            "torrent_id" : torrent_id,
            "created" : created,
            "size" : self.Handler.humanSize(self.RT.getSizeBytes(torrent_id)),
            "ratio" : "%.02f" % (float(self.RT.getRatio(torrent_id))/1000),
        }
        return json.dumps(jsonObject)
        
    def pause_torrent(self, torrent_id):
        try:
            self.RT.pause(torrent_id)
        except:
            return "ERROR"
        else:
            return "OK"
    
    def stop_torrent(self, torrent_id):
        try:
            self.RT.stop(torrent_id)
        except:
            return "ERROR"
        else:
            return "OK"
        
    def start_torrent(self, torrent_id):
        try:
            self.RT.resume(torrent_id)
        except:
            return "ERROR"
        else:
            return "OK"
        
    def remove_torrent(self, torrent_id):
        try:
            self.RT.remove(torrent_id)
        except:
            return "ERROR"
        else:
            return "OK"
        