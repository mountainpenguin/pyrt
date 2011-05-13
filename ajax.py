#/usr/bin/env python

import cgi
import rtorrent
import simplejson as json
import time

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
        self.uploaded = "%.02f" % (float(RT.getUploadBytes(torrent_id))/1024/1024)
        self.downloaded = "%.02f" % (float(RT.getDownloadBytes(torrent_id))/1024/1024)
        self.size = "%.02f" % (float(RT.getSizeBytes(torrent_id))/1024/1024)
        self.ratio = "%.02f" % (float(RT.getRatio(torrent_id))/1000)
        self.created = RT.conn.d.get_creation_date(torrent_id)
        self.trackers = []
        for x in range(100):
            try:
                self.trackers += [RT.conn.t.get_url(torrent_id, x)]
            except:
                break
        self.peers = []
        peer_exchange_len = RT.conn.d.get_peer_exchange(torrent_id)
        peers_accounted_len = RT.conn.d.get_peers_accounted(torrent_id)
        peers_complete_len = RT.conn.d.get_peers_complete(torrent_id)
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


def get_torrent_info(torrent_id):
    t = Torrent(torrent_id)
    c = time.localtime(t.created)
    created = "%02i/%02i/%i %02i:%02i:%02i" % (
        c.tm_mday,
        c.tm_mon,
        c.tm_year,
        c.tm_hour,
        c.tm_min,
        c.tm_sec,
    )
    jsonObject = {
        "name" : t.name,
        "uploaded" : t.uploaded,
        "downloaded" : t.downloaded,
        "trackers" : [
            "http://" + x.replace("http://","").split("/",1)[0] + "/..." for x in t.trackers
        ],
        "peers" : t.peers,
        "torrent_id" : t.torrent_id,
        "created" : created,
        "size" : t.size,
        "ratio" : t.ratio,
    }
    return json.dumps(jsonObject)
    

if __name__ == "__main__":
    form = cgi.FieldStorage()
    request = form.getfirst("request")
    RT = rtorrent.rtorrent("/home/torrent/.session/rpc.socket")
    
    if request == "get_torrent_info":
        t_id = form.getfirst("torrent_id")
        print "Content-type : text/plain\n"
        print get_torrent_info(t_id)
