#!/usr/bin/env python

#rtorrent class
import xmlrpc2scgi as xmlrpc
import xmlrpclib
import time
import sys
import os
import itertools

#usage
#import rtorrent
#RT = rtorrent.rtorrent(port)
#id = RT.getIDByName(downloadname)
#RT.wait_completed(id) # returns True

class Tracker:
    def __init__(self, url, type, interval, seeds, leechs, enabled):
        self.url = url
        self.type = type
        self.interval = interval
        self.seeds = seeds
        self.leechs = leechs
        self.enabled = enabled
class File:
    def __init__(self, abs_path, base_path, path_components, completed_chunks, priority, size, chunks, chunk_size):
        self.abs_path = abs_path
        self.base_path = base_path
        self.path_components = path_components
        self.completed_chunks = completed_chunks
        self.priority_int = priority
        self.priority = {0 : "off", 1 : "normal", 2 : "high"}[priority]
        self.size = size
        self.chunks = chunks
        self.chunk_size = chunk_size
        self.percentage_complete = 100 * (float(self.completed_chunks) / self.chunks)

class Peer:
    def __init__(self, address, client_version, completed_percent, down_rate, down_total, up_rate, up_total, port, peer_rate, peer_total):
        self.address = address
        self.client_version = client_version
        self.completed_percent = completed_percent
        self.down_rate = down_rate
        self.down_total = down_total
        self.up_rate = up_rate
        self.up_total = up_total
        self.port = port
        self.peer_rate = peer_rate
        self.peer_total = peer_total

class Torrent:
    def __init__(self, id, name, base_path, size_chunks, chunk_size, completed_bytes, creation_date, down_rate, up_rate, peers_connected, peers_total, seeders_connected, seeders_total, priority, ratio, size, up_total, down_total, status, private, trackers):
        self.torrent_id = id
        self.name = name
        self.base_path = base_path
        self.chunk_size = chunk_size
        self.completed_bytes = completed_bytes
        self.created = creation_date
        self.down_rate = down_rate
        self.down_total = down_total
        self.up_rate = up_rate
        self.up_total = up_total
        self.peers_connected = peers_connected
        self.peers_total = peers_total
        self.seeds_connected = seeders_connected
        self.seeds_total = seeders_total
        self.priority = priority
        self.priority_str = {0:"off", 1:"low", 2:"normal", 3:"high"}[priority]
        self.ratio = ratio
        self.size = size
        self.size_chunks = size_chunks
        self.status = status
        self.private = bool(private)
        self.trackers = trackers

class rtorrent:
    def __init__(self, port):
        if type(port) == int:
            self.port = port
        #test connection
            self.conn = xmlrpc.RTorrentXMLRPCClient("scgi://localhost:%i" % self.port)
        else:
            #path defined
            self.conn = xmlrpc.RTorrentXMLRPCClient(port)
        self.conn.system.listMethods()

    def getTorrentList2(self,view):
        torrentlist = self.conn.d.multicall(
            view,
            "d.get_hash=",
            "d.get_name=",
            "d.get_base_path=",
            "d.get_size_chunks=",
            "d.get_chunk_size=",
            "d.get_completed_bytes=",
            "d.get_creation_date=",
            "d.get_down_rate=",
            "d.get_up_rate=",
            "d.get_priority=",
            "d.get_ratio=",
            "d.get_size_bytes=",
            "d.get_up_total=",
            "d.get_down_total=",
            "d.is_private=",
            "d.get_peers_complete=",
            "d.get_peers_accounted=",
        )
        torrentList = []
        for tor in torrentlist:
            #deal with peers
            trackers = self.getTrackers(tor[0])
            peers_total = sum([i.leechs for i in trackers])
            seeds_total = sum([i.seeds for i in trackers])
            #deal with status
            status = self.getStateStr(tor[0])
            torrentList += [
                Torrent(
                    tor[0],
                    tor[1],
                    tor[2],
                    tor[3],
                    tor[4],
                    tor[5],
                    tor[6],
                    tor[7],
                    tor[8],
                    tor[16],
                    peers_total,
                    tor[15],
                    seeds_total,
                    tor[9],
                    tor[10],
                    tor[11],
                    tor[12],
                    tor[13],
                    status,
                    tor[14],
                    trackers
                )
            ]
#            0 "d.get_hash=","d.get_name=","d.get_base_path=","d.get_size_chunks=","d.get_chunk_size=", 4
#            5 "d.get_completed_bytes=","d.get_creation_date=","d.get_down_rate=","d.get_up_rate=", 8
#            9 "d.get_priority=","d.get_ratio=","d.get_size_bytes=","d.get_up_total=","d.get_down_total=", 13
#           14 "d.is_private=","d.get_peers_complete=","d.get_peers_accounted=", 16
        return torrentList
#id, name, base_path, size_chunks, chunk_size, completed_bytes, creation_date, down_rate, up_rate, peers_connected, peers_total, seeders_connected, seeders_total, priority, ratio, size, up_total, down_total, status, private

    def getTorrentList(self):
        torrentlist = self.conn.download_list("main")
        torrentdict = {}
        for i in torrentlist:
            name = self.getNameByID(i)
            torrentdict[i] = name
        return torrentdict
		
    def getTorrentInfo(self, id):
        #this is slower than the alternative
        allTorrents = self.getTorrentList2("main")
        for t in allTorrents:
            if t.torrent_id == id:
                return t

    def getIDByName(self, filename):
        alldownloads = self.conn.download_list("main")
        for id in alldownloads:
            name = self.conn.d.get_name(id)
            if name == filename:
                return id

    def getNameByID(self, id):
        count = 0
        while True:
            if count == 10:
                print "Timeout occurred"
            try:
                return self.conn.d.get_name(id)
            except TypeError:
                time.sleep(5)
            count += 1

    def getDownloadList(self):
        downloading = self.conn.download_list("incomplete")
        downloaddict = {}
        for i in downloading:
            name = self.getNameByID(i)
            downloaddict[i] = name
        return downloaddict
        
    def getRatio(self, id):
        ratio = self.conn.d.get_ratio(id)
        return ratio
    
    def getSizeBytes(self, id):
        size = self.conn.d.get_size_bytes(id)
        return size

    def getDownloadBytes(self, id):
        return self.conn.d.get_down_total(id)

    def getUploadBytes(self, id):
        return self.conn.d.get_up_total(id)

    def getDownloadSpeed(self, id):
        return self.conn.d.get_down_rate(id)

    def getUploadSpeed(self, id):
        return self.conn.d.get_up_rate(id)

    def getTrackers(self, id):
        trackers = []
        resp = self.conn.t.multicall(
            id,
            " ",
            "t.get_url=",               #tracker url
            "t.get_type=",              #tracker type, {1:"http", 2:"udp", 3:"dht"
            "t.get_normal_interval=",   #default announce interval
            "t.get_scrape_complete=",   #seeders registered on the tracker
            "t.get_scrape_incomplete=", #leechers registered on the tracker
            "t.is_enabled=",            #{0:"disabled", 1:"enabled"}
        )
        for track_resp in resp:
            trackers += [Tracker(track_resp[0], track_resp[1], track_resp[2], track_resp[3], track_resp[4], bool(track_resp[5]))]
#url, type, interval, seeds, leechs, enabled
        return trackers

    def getPeers(self, id):
        peers_connected = self.conn.d.get_peers_connected(id)
        peers = []
        if peers_connected > 0:
            resp = self.conn.p.multicall(
                id,
                " ",
                "p.get_address=",
                "p.get_port=",
                "p.get_client_version=",
                "p.get_completed_percent=",
                "p.get_down_rate=",
                "p.get_down_total=",
                "p.get_up_rate=",
                "p.get_up_total=",
                "p.get_peer_rate=",
                "p.get_peer_total=",
            )
            for element in resp:
                peers += [
                    Peer(element[0], element[2],
                         element[3], element[4],
                         element[5], element[6],
                         element[7], element[1],
                         element[8], element[9],)
                ]
#address, client_version, completed_percent, down_rate, down_total, up_rate, up_total, port, peer_rate, peer_total
        return peers

    def getFiles(self, id):
        files = []
        resp = self.conn.f.multicall(
            id,
            " ",
            "f.get_path_components=",
            "f.get_size_bytes=",
            "f.get_size_chunks=",
            "f.get_completed_chunks=",
            "f.get_priority=",
        )

        for file in resp:
            path_split = file[0]
            rel_path = "/".join(path_split)
            size_bytes = file[1]
            size_chunks = file[2]
            completed_chunks = file[3]
            chunk_size = self.conn.d.get_chunk_size(id)
            priority = file[4]
            base_path = self.getPath(id)
            absolute_path = os.path.join(base_path, rel_path)
            files += [File(absolute_path, base_path, path_split, completed_chunks, priority, size_bytes, size_chunks, chunk_size)]
        return files
#abs_path, base_path, path_components, completed_chunks, priority, size, chunks, chunk_size

    def getCreationDate(self, id):
        dat = self.conn.d.get_creation_date(id)
        dat_time = time.localtime(dat)
        return "%02i/%02i/%i %02i:%02i:%02i" % (
            dat_time.tm_mday,
            dat_time.tm_mon,
            dat_time.tm_year,
            dat_time.tm_hour,
            dat_time.tm_min,
            dat_time.tm_sec,
        )

    def getPath(self, id):
        return self.conn.d.get_directory(id)

    def getPriorityStr(self, id):
        return self.conn.d.get_priority_str(id)

    def getStateStr(self, id):
        act = self.conn.d.is_active(id)
        has = self.conn.d.is_hash_checking(id)
        ope = self.conn.d.is_open(id)
        #~ return "act:%s has:%s ope:%s" % (act, has, ope)
        if not ope and not act and not has:
            return "Stopped"
        elif ope and not act and not has:
            return "Paused"
        elif ope and not act and has:
            return "Hashing"
        elif ope and act and not has:
            return "Active"

    def getRootDir(self):
        return self.conn.get_directory()

    def getGlobalUpBytes(self):
        return self.conn.get_up_total()
    
    def getGlobalDownBytes(self):
        return self.conn.get_down_total()
    
    def getGlobalUpRate(self):
        return self.conn.get_up_rate()
    
    def getGlobalDownRate(self):
        return self.conn.get_down_rate()

    def getCreationDate(self, id):
        return self.conn.d.get_creation_date(torrent_id)
        
    def wait_completed(self, Id):
        time.sleep(2)
        
        while True:
            try:
                name = self.conn.d.get_name(id)
            except xmlrpclib.Fault:
                id = self.getIDByName(id)
            completed = self.conn.d.get_complete(id)
            if completed == 0:
                totalchunks = self.conn.d.get_size_chunks(id)
                completed = float(self.conn.d.get_completed_chunks(id))
                percentage = completed / totalchunks
                percentage = int(percentage * 100)
                time.sleep(2)
            else:
                print "100%"
                return True

                    
    def remove(self,id):
        self.conn.d.erase(id)
        
    def pause(self, id):
        self.conn.d.pause(id)
        
    def resume(self, id):
        if self.conn.d.is_open(id):
            self.conn.d.resume(id)
        else:
            self.conn.d.start(id)
        
    def stop(self, id):
        self.conn.d.stop(id)
        self.conn.d.close(id)