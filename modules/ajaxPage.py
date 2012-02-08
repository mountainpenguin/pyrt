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
import urlparse
import re
import urllib
import urllib2
import socket

from modules.Cheetah.Template import Template

class Ajax:
    def __init__(self, conf=config.Config()):
        self.Config = conf
        self.RT = rtorrent.rtorrent(self.Config.get("rtorrent_socket"))
        self.Handler = torrentHandler.Handler()
        self.Login = login.Login(conf=self.Config)
        
    def verify_conf_value(self, key, value):
        """
            keys:
                oldpass
                refreshrate
                pyrtport
                throttle-up
                throttle-down
                network-portfrom
                network-portto
                network-dir
                network-moveto
        """
        if key == "oldpass":
            if self.Login.checkPassword(value):
                return "RESPONSE/OK/OK"
            else:
                currpass = self.Config.get("password")
                salt = base64.b64decode(currpass.split("$")[1])
                return "RESPONSE/NO/Incorrect Password"
        elif key in ["refreshrate", "throttle-up", "throttle-down", "network-simuluploads", "network-simuldownloads","network-maxpeers","network-maxpeersseed","network-maxopensockets","network-maxopenhttp","performance-maxmemory","performance-maxfilesize","performance-maxopenfiles","performance-receivebuffer","performance-sendbuffer","performance-readahead"]:
            try:
                test = int(value)
                return "RESPONSE/OK/OK"
            except ValueError:
                return "RESPONSE/NO/Value must be an integer"
        elif key == "pyrtport":
            try:
                testport = int(value)
                s = socket.socket(socket.AF_INET)
                s.bind((self.Config.get("host"), testport))
            except ValueError:
                return "RESPONSE/NO/Value must be an integer"
            except socket.error as e:
                s.close()
                return "RESPONSE/NO/%s" % e
            else:
                s.close()
                return "RESPONSE/OK/OK"
        elif key in ["network-portfrom", "network-portto"]:
            try:
                testport = int(value)
            except ValueError:
                return "RESPONSE/NO/Value must be an integer"
            else:
                if testport > 65555:
                    return "RESPONSE/NO/Out of port range"
                elif testport < 1024:
                    return "RESPONSE/NO/Restricted port"
                else:
                    return "RESPONSE/OK/OK"
        elif key in ["general-dir","general-moveto"]:
            if os.path.exists(value):
                if not os.path.isdir(value):
                    return "RESPONSE/NO/Not a directory"
                elif not os.access(value, os.W_OK):
                    return "RESPONSE/NO/Insufficient permissions"
                else:
                    return "RESPONSE/OK/OK"
            else:
                return "RESPONSE/NO/No such path"
        else:
            return "RESPONSE/NO/Unknown key"
        
    def get_feeds(self):
        return "Nothing yet!"
    
    def _peerProcess(self, peer):
        peer.dlrate = self.Handler.humanSize(peer.down_rate)
        peer.dltot = self.Handler.humanSize(peer.down_total)
        peer.uprate = self.Handler.humanSize(peer.up_rate)
        peer.uptot = self.Handler.humanSize(peer.up_total)
        peer.rate = self.Handler.humanSize(peer.peer_rate)
        peer.total = self.Handler.humanSize(peer.peer_total)
        return peer.__dict__

    def get_torrent_info(self, torrent_id, html=None ):
        c = time.localtime(self.RT.getCreationDate(torrent_id))
        created = time.strftime("%d/%m/%Y %H:%M:%S", c)
        size = self.RT.getSizeBytes(torrent_id)
        completed_bytes = self.RT.getCompletedBytes(torrent_id)
        if completed_bytes >= size:
            completed = True
        else:
            completed = False
        peers = self.RT.getPeers(torrent_id)
        jsonObject = {
            "name" : self.RT.getNameByID(torrent_id),
            "uploaded" : self.Handler.humanSize(self.RT.getUploadBytes(torrent_id)),
            "downloaded" : self.Handler.humanSize(self.RT.getDownloadBytes(torrent_id)),
            "peers" : len(peers),
            "torrent_id" : torrent_id,
            "created" : created,
            "size" : self.Handler.humanSize(size),
            "ratio" : "%.02f" % (float(self.RT.getRatio(torrent_id))/1000),
            "percentage" : "%i" % ((float(self.RT.getCompletedBytes(torrent_id)) / size) * 100),
            "completed" : completed,
            "trackers" : [x.__dict__ for x in self.RT.getTrackers(torrent_id)],
            "peer_details" : [self._peerProcess(x) for x in peers],
            "file_tree" : self.Handler.fileTreeHTML(self.RT.getFiles(torrent_id), self.RT.getRootDir()),
        }
        if not html:
            return json.dumps(jsonObject)
        else:
            return Template(file="htdocs/dropDownHTML.tmpl", searchList=jsonObject).respond()
        
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
            
    def get_info_multi(self, view, sortby, reverse, drop_down_ids):
        drop_downs = {}
        if drop_down_ids:
            for t_id in drop_down_ids.split(","):
                drop_downs[t_id] = self.get_torrent_info(t_id, html="yes please")
        #wanted:
        #   system info
        #   ratio, dl speed, ul speed, status
        torrentList = self.Handler.sortTorrents(self.RT.getTorrentList2(view), sortby, reverse)
        returnDict = {
            "torrents" : {},
            "system" : system.get_global(encode_json=True),
            #"system" : base64.b64encode(system.generalHTML()),
            "torrent_index" : [x.torrent_id for x in torrentList],
            "drop_downs" : drop_downs,
            "drop_down_keys" : drop_downs.keys(),
        }
        for t in torrentList:
            if t.completed_bytes >= t.size:
                completed = True
                perc = None
            else:
                completed = False
                perc = int((float(t.completed_bytes) / t.size)*100)
            returnDict["torrents"][t.torrent_id] = {
                "ratio" : "%.02f" % (float(t.ratio)/1000),
                "uprate" : self.Handler.humanSize(t.up_rate),
                "downrate" : self.Handler.humanSize(t.down_rate),
                "status" : self.Handler.getState(t),
                "name" : t.name,
                "size" : self.Handler.humanSize(t.size),
                "up_total" : self.Handler.humanSize(t.up_total),
                "down_total" : self.Handler.humanSize(t.down_total),
                "completed" : completed,
                "percentage" : perc,
            }
        return json.dumps(returnDict)
        
    def get_torrent_row(self, torrent_id):
        torrentObj = self.RT.getTorrentObj_less(torrent_id)
        return self.Handler.getTorrentRow(torrentObj)
        
    def start_batch(self, torrentListStr):
        torrentList = torrentListStr.split(",")
        for torrent_id in torrentList:
            self.start_torrent(torrent_id)
            
    def pause_batch(self, torrentListStr):
        torrentList = torrentListStr.split(",")
        for torrent_id in torrentList:
            self.pause_torrent(torrent_id)
            
    def stop_batch(self, torrentListStr):
        torrentList = torrentListStr.split(",")
        for torrent_id in torrentList:
            self.stop_torrent(torrent_id)
            
    def remove_batch(self, torrentListStr):
        torrentList = torrentListStr.split(",")
        for torrent_id in torrentList:
            self.remove_torrent(torrent_id)
            
    def delete_batch(self, torrentListStr):
        torrentList = torrentListStr.split(",")
        for torrent_id in torrentList:
            self.delete_torrent(torrent_id)
            
    def get_tracker_favicon(self, torrentID):
        tracker_urls = [urlparse.urlparse(x.url) for x in self.RT.getTrackers(torrentID)]
        netloc = re.split(":\d+", tracker_urls[0].netloc)[0]
        scheme = tracker_urls[0].scheme
        try:
            test_fav = urllib2.urlopen("%s://%s/favicon.ico" % (scheme, netloc)).read()
        except urllib2.URLError as e:
            try:
                test_fav = urllib2.urlopen("%s://%s/favicon.ico" % (scheme, ".".join(netloc.split(".")[1:]))).read()
            except urllib2.URLError as e:
                return "ERROR '%s://%s/favicon.ico' [%s]" % (scheme, ".".join(netloc.split(".")[1:]), e.__repr__())
            else:
                return "<html><body><img src='data:image/x-icon;base64,%s'></body></html>" % base64.b64encode(test_fav)
        else:
            return "<html><body><img src='data:image/x-icon;base64,%s'></body></html>" % base64.b64encode(test_fav)
