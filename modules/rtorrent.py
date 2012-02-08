#!/usr/bin/env python

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

"""Available commands

system.listMethods
system.methodExist
system.methodHelp
system.methodSignature
system.multicall
system.shutdown
system.capabilities
system.getCapabilities
and
argument.0
argument.1
argument.2
argument.3
branch
call_download
cat
close_low_diskspace
close_untied
create_link
d.add_peer
d.check_hash
d.close
d.create_link
d.delete_link
d.delete_tied
d.erase
d.get_base_filename
d.get_base_path
d.get_bitfield
d.get_bytes_done
d.get_chunk_size
d.get_chunks_hashed
d.get_complete
d.get_completed_bytes
d.get_completed_chunks
d.get_connection_current
d.get_connection_leech
d.get_connection_seed
d.get_creation_date
d.get_custom
d.get_custom1
d.get_custom2
d.get_custom3
d.get_custom4
d.get_custom5
d.get_custom_throw
d.get_directory
d.get_directory_base
d.get_down_rate
d.get_down_total
d.get_free_diskspace
d.get_hash
d.get_hashing
d.get_hashing_failed
d.get_ignore_commands
d.get_left_bytes
d.get_loaded_file
d.get_local_id
d.get_local_id_html
d.get_max_file_size
d.get_max_size_pex
d.get_message
d.get_mode
d.get_name
d.get_peer_exchange
d.get_peers_accounted
d.get_peers_complete
d.get_peers_connected
d.get_peers_max
d.get_peers_min
d.get_peers_not_connected
d.get_priority
d.get_priority_str
d.get_ratio
d.get_size_bytes
d.get_size_chunks
d.get_size_files
d.get_size_pex
d.get_skip_rate
d.get_skip_total
d.get_state
d.get_state_changed
d.get_state_counter
d.get_throttle_name
d.get_tied_to_file
d.get_tracker_focus
d.get_tracker_numwant
d.get_tracker_size
d.get_up_rate
d.get_up_total
d.get_uploads_max
d.initialize_logs
d.is_active
d.is_hash_checked
d.is_hash_checking
d.is_multi_file
d.is_open
d.is_pex_active
d.is_private
d.multicall
d.open
d.pause
d.resume
d.save_session
d.set_connection_current
d.set_custom
d.set_custom1
d.set_custom2
d.set_custom3
d.set_custom4
d.set_custom5
d.set_directory
d.set_directory_base
d.set_hashing_failed
d.set_ignore_commands
d.set_max_file_size
d.set_message
d.set_peer_exchange
d.set_peers_max
d.set_peers_min
d.set_priority
d.set_throttle_name
d.set_tied_to_file
d.set_tracker_numwant
d.set_uploads_max
d.start
d.stop
d.try_close
d.try_start
d.try_stop
d.update_priorities
d.views
d.views.has
d.views.push_back
d.views.push_back_unique
d.views.remove
delete_link
dht
dht_add_node
dht_statistics
download_list
enable_trackers
encoding_list
encryption
event.download.closed
event.download.erased
event.download.finished
event.download.hash_done
event.download.hash_queued
event.download.hash_removed
event.download.inserted
event.download.inserted_new
event.download.inserted_session
event.download.opened
event.download.paused
event.download.resumed
execute
execute_capture
execute_capture_nothrow
execute_nothrow
execute_raw
execute_raw_nothrow
f.get_completed_chunks
f.get_frozen_path
f.get_last_touched
f.get_match_depth_next
f.get_match_depth_prev
f.get_offset
f.get_path
f.get_path_components
f.get_path_depth
f.get_priority
f.get_range_first
f.get_range_second
f.get_size_bytes
f.get_size_chunks
f.is_create_queued
f.is_created
f.is_open
f.is_resize_queued
f.multicall
f.set_create_queued
f.set_priority
f.set_resize_queued
f.unset_create_queued
f.unset_resize_queued
false
fi.get_filename_last
fi.is_file
get_bind
get_check_hash
get_connection_leech
get_connection_seed
get_dht_port
get_dht_throttle
get_directory
get_down_rate
get_down_total
get_download_rate
get_handshake_log
get_hash_interval
get_hash_max_tries
get_hash_read_ahead
get_http_cacert
get_http_capath
get_http_proxy
get_ip
get_key_layout
get_log.tracker
get_max_downloads_div
get_max_downloads_global
get_max_file_size
get_max_memory_usage
get_max_open_files
get_max_open_http
get_max_open_sockets
get_max_peers
get_max_peers_seed
get_max_uploads
get_max_uploads_div
get_max_uploads_global
get_memory_usage
get_min_peers
get_min_peers_seed
get_name
get_peer_exchange
get_port_open
get_port_random
get_port_range
get_preload_min_size
get_preload_required_rate
get_preload_type
get_proxy_address
get_receive_buffer_size
get_safe_free_diskspace
get_safe_sync
get_scgi_dont_route
get_send_buffer_size
get_session
get_session_lock
get_session_on_completion
get_split_file_size
get_split_suffix
get_stats_not_preloaded
get_stats_preloaded
get_throttle_down_max
get_throttle_down_rate
get_throttle_up_max
get_throttle_up_rate
get_timeout_safe_sync
get_timeout_sync
get_tracker_numwant
get_up_rate
get_up_total
get_upload_rate
get_use_udp_trackers
get_xmlrpc_size_limit
greater
group.insert
group.insert_persistent_view
group.seeding.ratio.command
group.seeding.ratio.disable
group.seeding.ratio.enable
group.seeding.ratio.max
group.seeding.ratio.max.set
group.seeding.ratio.min
group.seeding.ratio.min.set
group.seeding.ratio.upload
group.seeding.ratio.upload.set
group.seeding.view
group.seeding.view.set
if
import
less
load
load_raw
load_raw_start
load_raw_verbose
load_start
load_start_verbose
load_verbose
log.execute
log.xmlrpc
not
on_close
on_erase
on_finished
on_hash_queued
on_hash_removed
on_insert
on_open
on_ratio
on_start
on_stop
or
p.get_address
p.get_client_version
p.get_completed_percent
p.get_down_rate
p.get_down_total
p.get_id
p.get_id_html
p.get_options_str
p.get_peer_rate
p.get_peer_total
p.get_port
p.get_up_rate
p.get_up_total
p.is_encrypted
p.is_incoming
p.is_obfuscated
p.is_snubbed
p.multicall
print
ratio.disable
ratio.enable
ratio.max
ratio.max.set
ratio.min
ratio.min.set
ratio.upload
ratio.upload.set
remove_untied
scgi_local
scgi_port
schedule
schedule_remove
scheduler.max_active
scheduler.max_active.set
scheduler.simple.added
scheduler.simple.removed
scheduler.simple.update
session_save
set_bind
set_check_hash
set_connection_leech
set_connection_seed
set_dht_port
set_dht_throttle
set_directory
set_download_rate
set_handshake_log
set_hash_interval
set_hash_max_tries
set_hash_read_ahead
set_http_cacert
set_http_capath
set_http_proxy
set_ip
set_key_layout
set_log.tracker
set_max_downloads_div
set_max_downloads_global
set_max_file_size
set_max_memory_usage
set_max_open_files
set_max_open_http
set_max_open_sockets
set_max_peers
set_max_peers_seed
set_max_uploads
set_max_uploads_div
set_max_uploads_global
set_min_peers
set_min_peers_seed
set_name
set_peer_exchange
set_port_open
set_port_random
set_port_range
set_preload_min_size
set_preload_required_rate
set_preload_type
set_proxy_address
set_receive_buffer_size
set_safe_sync
set_scgi_dont_route
set_send_buffer_size
set_session
set_session_lock
set_session_on_completion
set_split_file_size
set_split_suffix
set_timeout_safe_sync
set_timeout_sync
set_tracker_numwant
set_upload_rate
set_use_udp_trackers
set_xmlrpc_size_limit
start_tied
stop_untied
system.client_version
system.file_allocate
system.file_allocate.set
system.file_status_cache.prune
system.file_status_cache.size
system.get_cwd
system.hostname
system.library_version
system.method.erase
system.method.get
system.method.has_key
system.method.insert
system.method.list_keys
system.method.set
system.method.set_key
system.pid
system.set_cwd
system.set_umask
system.time
system.time_seconds
system.time_usec
t.get_group
t.get_id
t.get_min_interval
t.get_normal_interval
t.get_scrape_complete
t.get_scrape_downloaded
t.get_scrape_incomplete
t.get_scrape_time_last
t.get_type
t.get_url
t.is_enabled
t.is_open
t.multicall
t.set_enabled
test.method.simple
throttle_down
throttle_ip
throttle_up
to_date
to_elapsed_time
to_gm_date
to_gm_time
to_kb
to_mb
to_throttle
to_time
to_xb
tos
try_import
ui.current_view.set
ui.unfocus_download
view.event_added
view.event_removed
view.filter_download
view.persistent
view.set_not_visible
view.set_visible
view.size
view.size_not_visible
view_add
view_filter
view_filter_on
view_list
view_set
view_sort
view_sort_current
view_sort_new
xmlrpc_dialect

"""

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
        self.priority_str = {-1 : None, 0:"off", 1:"low", 2:"normal", 3:"high"}[priority]
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
                        except urllib2.URLError:
                            fav_icon_url2 = "%s://%s/favicon.ico" % (url_parsed.scheme, ".".join(root_url.split(".")[1:]))
                            print fav_icon_url2
                            try:
                                fav_icon = urllib2.urlopen(fav_icon_url2, timeout=2).read()
                                open("static/favicons/%s.ico" % (root_url),"wb").write(fav_icon)
                            except urllib2.URLError:
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
        
    def getGlobalRootPath(self):
        return self.conn.get_directory()
        
    def getGlobalPortRange(self):
        return self.conn.get_port_range()

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
        
    def getGlobalUpThrottle(self):
        return self.conn.get_upload_rate()
        
    def getGlobalDownThrottle(self):
        return self.conn.get_download_rate()

    def getCreationDate(self, id):
        return self.conn.d.get_creation_date(id)
        
    def getCompletedBytes(self, id):
        return self.conn.d.get_completed_bytes(id)
        
    def getGlobalMaxMemoryUsage(self):
        return self.conn.get_max_memory_usage()

    def getGlobalSendBufferSize(self):
        return self.conn.get_send_buffer_size()
        
    def getGlobalReceiveBufferSize(self):
        return self.conn.get_receive_buffer_size()
        
    def getGlobalHashReadAhead(self):
        return self.conn.get_hash_read_ahead()
        
    def getGlobalMaxDownloads(self):
        return self.conn.get_max_downloads_global()
    
    def getGlobalMaxUploads(self):
        return self.conn.get_max_uploads_global()
        
    def getGlobalMaxPeers(self):
        return self.conn.get_max_peers()
        
    def getGlobalMaxPeersSeed(self):
        return self.conn.get_max_peers_seed()
        
    def getGlobalMaxOpenSockets(self):
        return self.conn.get_max_open_sockets()
        
    def getGlobalMaxOpenHttp(self):
        return self.conn.get_max_open_http()
        
    def getGlobalMaxFileSize(self):
        return self.conn.get_max_file_size()
        
    def getGlobalMaxOpenFiles(self):
        return self.conn.get_max_open_files()
        
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
       
