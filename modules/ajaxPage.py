#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi
import rtorrent
try:
    import simplejson as json
except ImportError:
    import json
import time
import torrentHandler
import login
import os
import sys
import config
import shutil
import bencode
import system
import base64

class Ajax:
    def __init__(self):
        self.Config = config.Config()
        self.RT = rtorrent.rtorrent(self.Config.get("rtorrent_socket"))
        self.Handler = torrentHandler.Handler()
        
    def get_torrent_info(self, torrent_id, html=None ):
        c = time.localtime(self.RT.getCreationDate(torrent_id))
        created = time.strftime("%d/%m/%Y %H:%M:%S", c)
        size = self.RT.getSizeBytes(torrent_id)
        jsonObject = {
            "name" : self.RT.getNameByID(torrent_id),
            "uploaded" : self.Handler.humanSize(self.RT.getUploadBytes(torrent_id)),
            "downloaded" : self.Handler.humanSize(self.RT.getDownloadBytes(torrent_id)),
            "peers" : len(self.RT.getPeers(torrent_id)),
            "torrent_id" : torrent_id,
            "created" : created,
            "size" : self.Handler.humanSize(size),
            "ratio" : "%.02f" % (float(self.RT.getRatio(torrent_id))/1000),
            "percentage" : "%i" % ((float(self.RT.getCompletedBytes(torrent_id)) / size) * 100),
        }
        if not html:
            return json.dumps(jsonObject)
        else:
            return """
                <div class='drop_down'>
                    <div class='column-1'>ID:</div><div class='column-2'>%(torrent_id)s</div>
                    <div class='column-1'>Size:</div><div class='column-2'>%(size)s</div>
                    <div class='column-1'>Percentage:</div><div class='column-2'>%(percentage)s%%</div>
                    <div class='column-1'>Downloaded:</div><div class='column-2'>%(downloaded)s</div>
                    <div class='column-1'>Uploaded:</div><div class='column-2'>%(uploaded)s</div>
                    <div class='column-1'>Ratio:</div><div class='column-2'>%(ratio)s</div>
                    <div class='column-1'>Peers:</div><div class='column-2'>%(peers)s</div>
                    <div class='column-1'>Created:</div><div class='column-2'>%(created)s</div>
                    <div class='column-2' style='clear : left;'><span class='fakelink' onClick='removerow("%(torrent_id)s")'>Close</span> <a style='color : blue;' href='detail?torrent_id=%(torrent_id)s'>Detailed View</a></div>
                </div>
            """ % jsonObject
        
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

    def hash_torrent(self, torrent_id):
        try:
            self.RT.rehash(torrent_id)
        except:
            return "ERROR"
        else:
            return "OK"
            
    def delete_torrent(self, torrent_id):
        response = self.stop_torrent(torrent_id)
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
                    self.remove_torrent(torrent_id)
                    return "OK"
                except:
                    return "ERROR/unknown"
        else:
            return "ERROR/could not stop torrent"

    def get_file(self, torrent_id, filepath):
        files = self.RT.getFiles(torrent_id)
        fileOK = False
        completeOK = False
        for file in files:
            if file.abs_path == filepath:
                fileOK = True
                if int(file.percentage_complete) == 100:
                    completeOK = True
                break
        if not fileOK:
            return "ERROR/File doesn't exist"
        if not completeOK:
            return "ERROR/File not complete"
        fileContents = open(filepath).read()
        return fileContents
    
    def upload_torrent(self, torrent=None, start=None):
        fileName = unicode(torrent.filename)
        inFile = torrent.file.read()
        try:
            decoded = bencode.bdecode(inFile)
        except:
            #Invalid torrent
            print fileName
            return "ERROR/Invalid torrent file"
        else:
            #save file in /torrents
            newFile = open("torrents/%s" % (fileName.encode("utf-8")), "wb")
            newFile.write(inFile)
            newFile.close()
            #add file to rtorrent
            if start:
                self.RT.start_from_file(os.path.join(os.getcwd(), "torrents/%s" % fileName))
            else:
                self.RT.load_from_file(os.path.join(os.getcwd(), "torrents/%s" % fileName))
            return self.Handler.HTMLredirect("/")
            
    def get_info_multi(self, view, sortby, reverse):
        #wanted:
        #   system info
        #   ratio, dl speed, ul speed, status
        torrentList = self.Handler.sortTorrents(self.RT.getTorrentList2(view), sortby, reverse)
        returnDict = {
            "torrents" : {},
            "system" : system.generalHTML(),
            #"system" : base64.b64encode(system.generalHTML()),
            "torrent_index" : [x.torrent_id for x in torrentList],
        }
        for t in torrentList:
            returnDict["torrents"][t.torrent_id] = {
                "ratio" : "%.02f" % (float(t.ratio)/1000),
                "uprate" : self.Handler.humanSize(t.up_rate),
                "downrate" : self.Handler.humanSize(t.down_rate),
                "status" : self.Handler.getState(t)
            }
        return json.dumps(returnDict)
        
    def get_torrent_row(self, torrent_id):
        torrentObj = self.RT.getTorrentObj_less(torrent_id)
        return self.Handler.getTorrentRow(torrentObj)
        
                
        
