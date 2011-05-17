#!/usr/bin/env python

import cgi
import rtorrent
import simplejson as json
import time
import torrentHandler
import login
import os
import sys
import config
import shutil

class Ajax:
    def __init__(self):
        self.Config = config.Config()
        self.RT = rtorrent.rtorrent(self.Config.get("rtorrent_socket"))
        self.Handler = torrentHandler.Handler()
        
    def get_torrent_info(self, torrent_id):
        c = time.localtime(self.RT.getCreationDate(torrent_id))
        created = time.strftime("%d/%m/%Y %H:%M:%S", c)
        jsonObject = {
            "name" : self.RT.getNameByID(torrent_id),
            "uploaded" : self.Handler.humanSize(self.RT.getUploadBytes(torrent_id)),
            "downloaded" : self.Handler.humanSize(self.RT.getDownloadBytes(torrent_id)),
            "peers" : [x.__dict__ for x in self.RT.getPeers(torrent_id)],
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
                
    def delete_torrent(self, torrent_id):
        response = self.remove_torrent(torrent_id)
        if response == "OK":
            files = self.RT.getFiles(torrent_id)
            if len(files) == 1:
                #single file
                if files[0].base_path == self.RT.getRootDir():
                    delete = files[0].abs_path
            else:
                delete = files[0].base_path
            
            if not os.path.exists(delete):
                return "ERROR/no such file"
            else:
                try:
                    if os.path.isfile(delete):
                        os.remove(delete)
                    else:
                        shutil.rmtree(delete)
                except:
                    return "ERROR/unknown"
        else:
            return "ERROR/could not remove torrent"
