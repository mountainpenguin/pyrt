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

#rtorrent class
import xmlrpc2scgi as xmlrpc
import xmlrpclib
import time
import sys
import os
import itertools
import base64
import urllib2
import urlparse
import re

class Tracker(object):
    def __init__(self, url, type, interval, seeds, leechs, enabled, favicon, root_url):
        self.url = url
        self.type = type
        self.interval = interval
        self.seeds = seeds
        self.leechs = leechs
        self.enabled = enabled
        self.favicon_url = favicon
        self.root_url = root_url
class File(object):
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
        try:
            self.percentage_complete = 100 * (float(self.completed_chunks) / self.chunks)
        except:
            self.percentage_complete = 100.0

class Peer(object):
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

class Torrent(object):
    def __init__(self, id=None, name=None, base_path=None, size_chunks=None, chunk_size=None, completed_bytes=None, creation_date=None, down_rate=None, up_rate=None, peers_connected=None, peers_total=None, seeders_connected=None, seeders_total=None, priority=None, ratio=None, size=None, up_total=None, down_total=None, status=None, private=None, trackers=None):
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
        if self.priority:
            self.priority_str = {-1 : None, 0:"off", 1:"low", 2:"normal", 3:"high"}[priority]
        else:
            self.priority_str = None
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

    def getTorrentList(self):
        """
            Gets the 'main' rtorrent view
            
            Inputs:
                None
            Outputs:
                dictionary with torrent names indexed by torrent ids
                { ID : NAME }
        """
        torrentlist = self.conn.download_list("main")
        torrentdict = {}
        for i in torrentlist:
            name = self.getNameByID(i)
            torrentdict[i] = name
        return torrentdict
    
    def getTorrentStats(self,view="main"):
        """Returns information required for making /stats infographic pie charts

            returns a list of Torrent objects with attributes:
                hash, name, up_total, down_total, ratio, trackers
        """
        torrentlist = self.conn.d.multicall(
            view,
            "d.get_hash=",
            "d.get_name=",
            "d.get_up_total=",
            "d.get_down_total=",
            "d.get_ratio=",
        )
        torrentL = []
        for t in torrentlist:
            trackers = self.getTrackers(t[0])
            torrentL += [
                Torrent(
                    name = t[1],
                    up_total = t[2],
                    down_total = t[3],
                    ratio = t[4],
                    trackers = trackers,
                )
            ]
        return torrentL

    def getTorrentList2(self,view="main"):
        """
            More developed version of getTorrentList
            Gets any of the rtorrent views, for each torrent it gets the following attributes:
                
                hash, name, base_path, size_chunks, chunk_size, completed_bytes,
                creation_date, down_rate, up_rate, priority, ratio, size_bytes,
                up_total, down_total, is_private, peers_complete, peers_accounted
            
            Additionally it retrieves tracker information
            It returns this information in the form of a list of Torrent objects
        """
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


    
    def getTorrentInfo(self, id):
        #this is slower than the alternative
        allTorrents = self.getTorrentList2("main")
        for t in allTorrents:
            if t.torrent_id == id:
                return t
                
    def getTorrentObj_less(self, id):
        """
            returns a 'summarised' torrent object
            the torrent object returned by this function has attributes:
                torrent_id, name, up_rate, up_total, 
                down_rate, down_total, ratio, size, status
            i.e. only information required by torrentHandler.getTorrentRow
        """
        return Torrent(
            id,
            self.getNameByID(id),
            None, None, None, None, None,
            self.getDownloadSpeed(id),
            self.getUploadSpeed(id),
            None, None, None, None, -1,
            self.getRatio(id),
            self.getSizeBytes(id),
            self.getUploadBytes(id),
            self.getDownloadBytes(id),
            self.getStateStr(id),
            None, None
        )

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
            "",
            "t.get_url=",               #tracker url
            "t.get_type=",              #tracker type, {1:"http", 2:"udp", 3:"dht"
            "t.get_normal_interval=",   #default announce interval
            "t.get_scrape_complete=",   #seeders registered on the tracker
            "t.get_scrape_incomplete=", #leechers registered on the tracker
            "t.is_enabled=",            #{0:"disabled", 1:"enabled"}
        )
        for track_resp in resp:
            url = track_resp[0]
            if url == "dht://":
                faviconurl = "/favicons/dht.ico"
                root_url = "DHT"
            else:
                url_parsed = urlparse.urlparse(url)
                root_url = re.split(":\d+", url_parsed.netloc)[0]
                if "http" not in url_parsed.scheme:
                    fav_icon = None
                else:
                    if os.path.exists("static/favicons/%s.ico" % root_url):
                        fav_icon = True
                    else:
                        fav_icon_url = "%s://%s/favicon.ico" % (url_parsed.scheme, root_url)
                        try:
                            fav_icon = urllib2.urlopen(fav_icon_url, timeout=2).read()
                            open("static/favicons/%s.ico" % (root_url),"wb").write(fav_icon)
                        except:
                            fav_icon_url2 = "%s://%s/favicon.ico" % (url_parsed.scheme, ".".join(root_url.split(".")[1:]))
                            print fav_icon_url2
                            try:
                                fav_icon = urllib2.urlopen(fav_icon_url2, timeout=2).read()
                                open("static/favicons/%s.ico" % (root_url),"wb").write(fav_icon)
                            except:
                                fav_icon = None
                if fav_icon == None:
                    try:
                        os.symlink("default.ico", "static/favicons/%s.ico" % root_url)
                    except:
                        pass
                    faviconurl = "/favicons/default.ico"
                else:
                    faviconurl = "/favicons/%s.ico" % root_url
            trackers += [Tracker(track_resp[0], track_resp[1], track_resp[2], track_resp[3], track_resp[4], bool(track_resp[5]), faviconurl, root_url)]
#url, type, interval, seeds, leechs, enabled
        return trackers

    def getPeers(self, id):
        peers_connected = self.conn.d.get_peers_connected(id)
        peers = []
        if peers_connected > 0:
            resp = self.conn.p.multicall(
                id,
                "",
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
            "",
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

    #def getCreationDate(self, id):
    #    dat = self.conn.d.get_creation_date(id)
    #    dat_time = time.localtime(dat)
    #    return "%02i/%02i/%i %02i:%02i:%02i" % (
    #        dat_time.tm_mday,
    #        dat_time.tm_mon,
    #        dat_time.tm_year,
    #        dat_time.tm_hour,
    #        dat_time.tm_min,
    #        dat_time.tm_sec,
    #    )

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

    def getCreationDate(self, id):
        return self.conn.d.get_creation_date(id)
        
    def getCompletedBytes(self, id):
        return self.conn.d.get_completed_bytes(id)
        
    ### START 'GLOBAL' FUNCTIONS ###
    def getRootDir(self):
        return self.conn.get_directory()
        
    def getGlobalRootPath(self):
        return self.conn.get_directory()
        
    def setGlobalRootPath(self, path):
        #edit .rtorrent.rc?
        return self.conn.set_directory(path)
        
    def getGlobalPortRange(self):
        return self.conn.get_port_range()
        
    def setGlobalPortRange(self, range):
        return self.conn.set_port_range(range)

    def getGlobalUpBytes(self):
        return self.conn.get_up_total()
    
    def getGlobalDownBytes(self):
        return self.conn.get_down_total()
    
    def getGlobalUpRate(self):
        return self.conn.get_up_rate()
    
    def getGlobalDownRate(self):
        return self.conn.get_down_rate()
        
    def getGlobalUpThrottle(self):
        return self.conn.get_upload_rate()
        
    def setGlobalUpThrottle(self, throttle):
        #throttle must be in bytes
        return self.conn.set_upload_rate(throttle)
        
    def getGlobalDownThrottle(self):
        return self.conn.get_download_rate()
        
    def setGlobalDownThrottle(self, throttle):
        return self.conn.set_download_rate(throttle)
        
    def getGlobalMaxMemoryUsage(self):
        return self.conn.get_max_memory_usage()
        
    def setGlobalMaxMemoryUsage(self, mem):
        #mem in bytes
        #convert to str to allow large values
        return self.conn.set_max_memory_usage(str(mem))

    def getGlobalSendBufferSize(self):
        return self.conn.get_send_buffer_size()
        
    def setGlobalSendBufferSize(self, buffer):
        #buffer in bytes -> converted to str
        return self.conn.set_send_buffer_size(str(buffer))
        
    def getGlobalReceiveBufferSize(self):
        return self.conn.get_receive_buffer_size()
        
    def setGlobalReceiveBufferSize(self, buffer):
        return self.conn.set_receive_buffer_size(str(buffer))
        
    def getGlobalHashReadAhead(self):
        return self.conn.get_hash_read_ahead()
        
    def setGlobalHashReadAhead(self, readahead):
        return self.conn.set_hash_read_ahead(str(readahead))
        
    def getGlobalMaxDownloads(self):
        return self.conn.get_max_downloads_global()
        
    def setGlobalMaxDownloads(self, max):
        return self.conn.set_max_downloads_global(max)
    
    def getGlobalMaxUploads(self):
        return self.conn.get_max_uploads_global()
        
    def setGlobalMaxUploads(self, max):
        return self.conn.set_max_uploads_global(max)
        
    def getGlobalMaxPeers(self):
        return self.conn.get_max_peers()
        
    def setGlobalMaxPeers(self, peers):
        return self.conn.set_max_peers(peers)
        
    def getGlobalMaxPeersSeed(self):
        return self.conn.get_max_peers_seed()
        
    def setGlobalMaxPeersSeed(self, peers):
        return self.conn.set_max_peers_seed(peers)
        
    def getGlobalMaxOpenSockets(self):
        return self.conn.get_max_open_sockets()
        
    def setGlobalMaxOpenSockets(self, sockets):
        return self.conn.set_max_open_sockets(sockets)
        
    def getGlobalMaxOpenHttp(self):
        return self.conn.get_max_open_http()
    
    def setGlobalMaxOpenHttp(self, http):
        return self.conn.set_max_open_http(http)
        
    def getGlobalMaxFileSize(self):
        return self.conn.get_max_file_size()
        
    def setGlobalMaxFileSize(self, size):
        #size must be in bytes
        #converting size to a str to avoid XML-RPC complaining about long ints
        return self.conn.set_max_file_size(str(size))
        
    def getGlobalMaxOpenFiles(self):
        return self.conn.get_max_open_files()
        
    def setGlobalMaxOpenFiles(self, files):
        return self.conn.set_max_open_files(files)
        
    ### END 'GLOBAL' FUNCTIONS ###
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
        
    def rehash(self, id):
        self.conn.d.check_hash(id)
        
    def start_from_file(self, filepath):
        self.conn.load_start_verbose(filepath)
        
    def load_from_file(self, filepath):
        self.conn.load_verbose(filepath)