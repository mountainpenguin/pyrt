#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

from __future__ import print_function
import cgi
try:
    import simplejson as json
except ImportError:
    import json
import time
import os
import sys
import shutil
import bencode
import base64
import urlparse
import re
import urllib
import urllib2
import socket
import traceback
import logging

from modules.Cheetah.Template import Template
from modules import rtorrent, torrentHandler, login
from modules import config, system, weblog

class Handle(object):
    def __init__(self, handler, need_args=[], opt_args=[]):
        self.run = handler
        self.need_args = need_args
        self.opt_args = opt_args
        
class Ajax:
    def __init__(self, conf=config.Config(), RT=None, Log=None):
        self.Config = conf
        if not RT:
            self.RT = rtorrent.rtorrent(self.Config.get("rtorrent_socket"))
        else:
            self.RT = RT
        self.Handler = torrentHandler.Handler()
        self.Login = login.Login(conf=self.Config)
        self.Log = Log
        self.public_commands = {
            "get_torrent_info" : Handle(self.get_torrent_info, ["torrent_id"], ["html"]),
            "get_info_multi" : Handle(self.get_info_multi, ["view"], ["sortby", "reverse", "drop_down_ids"]),
            "get_torrent_row" : Handle(self.get_torrent_row, ["torrent_id"]),
            "pause_torrent" : Handle(self.pause_torrent, ["torrent_id"]),
            "stop_torrent" : Handle(self.stop_torrent, ["torrent_id"]),
            "start_torrent" : Handle(self.start_torrent, ["torrent_id"]),
            "remove_torrent" : Handle(self.remove_torrent, ["torrent_id"]),
            "delete_torrent" : Handle(self.delete_torrent, ["torrent_id"]),
            "hash_torrent" : Handle(self.hash_torrent, ["torrent_id"]),
            "get_file" : Handle(self.get_file, ["torrent_id", "filepath"]),
            "upload_torrent_socket" : Handle(self.upload_torrent_socket, ["torrent"], ["start"]),
            "upload_torrent" : Handle(self.upload_torrent, [], ["torrent", "start"]),
            "get_feeds" : Handle(self.get_feeds),
            "start_batch" : Handle(self.start_batch, ["torrentIDs"]),
            "pause_batch" : Handle(self.pause_batch, ["torrentIDs"]),
            "stop_batch" : Handle(self.stop_batch, ["torrentIDs"]),
            "remove_batch" : Handle(self.remove_batch, ["torrentIDs"]),
            "delete_batch" : Handle(self.delete_batch, ["torrentIDs"]),
            "get_tracker_favicon" : Handle(self.get_tracker_favicon, ["torrent_id"]),
            "verify_conf_value" : Handle(self.verify_conf_value, ["key", "value"]),
            "set_config_multiple" : Handle(self.set_config_multiple, ["keys","values"]),
        }
        
    def has_command(self, commandstr):
        if commandstr.lower() in self.public_commands:
            return True
        else:
            self.Log.error("AJAX: unknown command '%s'", commandstr)
            return False
        
    def validate_command(self, commandstr, parsed_queries):
        req_args = self.public_commands[commandstr.lower()].need_args
        opt_args = self.public_commands[commandstr.lower()].opt_args
        for r_a in req_args:
            if r_a not in parsed_queries or not parsed_queries[r_a]:
                self.Log.error("AJAX: too few arguments for request '%s'", commandstr)
                return False
        return True
            
    def handle(self, commandstr, qs):
        req_args = self.public_commands[commandstr.lower()].need_args
        opt_args = self.public_commands[commandstr.lower()].opt_args
        r_args = [qs.get(x, [None])[0] for x in req_args]
        o_args = {}
        for x in opt_args:
            y = qs.get(x, "nosucharg")
            if y != "nosucharg": #allow None, False, 0, etc.
                o_args[x] = y
                
        return self.public_commands[commandstr.lower()].run(*r_args, **o_args)
    
    def mbtob(self, value):
        """
            Converts MiB to B
        """
        return int(value)*1024*1024
        
    def kbtob(self, value):
        """
            Converts KiB to B
        """
        return int(value)*1024
        
    def throttleUp(self, value):
        self.Log.info("AJAX: global upload throttle set to %s", value)
        return self.RT.setGlobalUpThrottle(self.kbtob(value))
        
    def throttleDown(self, value):
        self.Log.info("AJAX: global download throttle set to %s", value)
        return self.RT.setGlobalDownThrottle(self.kbtob(value))
        
    def maxFileSize(self, value):
        self.Log.info("AJAX: global max file size set to %s", value)
        return self.RT.setGlobalMaxFileSize(self.mbtob(value))
        
    def mem(self, value):
        self.Log.info("AJAX: global max memory usage set to %s", value)
        return self.RT.setGlobalMaxMemoryUsage(self.mbtob(value))
        
    def rBuffer(self, value):
        self.Log.info("AJAX: global receive buffer size set to %sB (%sKiB)", self.kbtob(value), value)
        return self.RT.setGlobalReceiveBufferSize(self.kbtob(value))
        
    def sBuffer(self, value):
        self.Log.info("AJAX: global send buffer size set to %sB (%sKiB)", self.kbtob(value), value)
        return self.RT.setGlobalSendBufferSize(self.kbtob(value))
        
    def readahead(self, value):
        self.Log.info("AJAX: global hash readahead size set to %sB (%sMiB)", self.mbtob(value), value)
        return self.RT.setGlobalHashReadAhead(self.mbtob(value))
        
    def set_config_multiple(self, keys, values):
        """
            pyrt-oldpass
            pyrt-newpass
            pyrt-newpassconf
            pyrt-refreshrate
            pyrt-port
            general-dir
            general-moveto
            general-stopat
            throttle-up
            throttle-down
            network-portfrom
            network-portto
            network-simuluploads
            network-simuldownloads
            network-maxpeers
            network-maxpeersseed
            network-maxopensockets
            network-maxopenhttp
            performance-maxmemory
            performance-maxfilesize
            performance-maxopenfiles
            performance-receivebuffer
            performance-sendbuffer
            performance-readahead
        """
        actions = {
            #key : function
            #"pyrt-refreshrate" : ,
            #"pyrt-port" : ,
            "general-dir" : self.RT.setGlobalRootPath,
            "throttle-up" : self.throttleUp,
            "throttle-down" : self.throttleDown,
            "network-simuluploads" : self.RT.setGlobalMaxUploads,
            "network-simuldownloads" : self.RT.setGlobalMaxDownloads,
            "network-maxpeers" : self.RT.setGlobalMaxPeers,
            "network-maxpeersseed" : self.RT.setGlobalMaxPeersSeed,
            "network-maxopensockets" : self.RT.setGlobalMaxOpenSockets,
            "network-maxopenhttp" : self.RT.setGlobalMaxOpenHttp,
            "performance-maxmemory" : self.mem,
            "performance-maxfilesize" : self.maxFileSize,
            "performance-maxopenfiles" : self.RT.setGlobalMaxOpenFiles,
            "performance-receivebuffer" : self.rBuffer,
            "performance-sendbuffer" : self.sBuffer,
            "performance-readahead" : self.RT.setGlobalHashReadAhead,
        }
        #"pyrt-refreshrate": "unknown", "pyrt-newpass": "unknown", "pyrt-newpassconf": "unknown", "pyrt-oldpass": "unknown", "pyrt-port": "unknown"
        
        responses = {}
        
        ks = keys.split(",")
        vs = values.split(",")
        kvdict = dict([(ks[i], urllib.unquote(vs[i])) for i in range(len(ks))])
        for i in range(len(ks)):
            k = ks[i]
            v = urllib.unquote(vs[i])
            if k in actions.keys():
                try:
                    responses[k] = actions[k](v)
                except:
                    traceback.print_exc()
                    responses[k] = "error"
            elif k == "pyrt-newpassconf":
                if "pyrt-newpass" in ks and "pyrt-oldpass" in ks:
                    responses[k] = "ok"
                else:
                    responses[k] = "error required: pyrt-oldpass, pyrt-newpass"
            elif k == "network-portto":
                #require network-portto & network-portfrom
                if "network-portto" in ks and "network-portfrom" in ks:
                    responses["network-port"] = self.RT.setGlobalPortRange("%s-%s" % (kvdict["network-portfrom"], kvdict["network-portto"]))
                else:
                    responses[k] = "error required: network-portto, network-portfrom"
            elif k == "general-moveto":
                responses[k] = "recognised"
            elif k == "general-stopat":
                responses[k] = "recognised"
            elif k in ["pyrt-newpass", "pyrt-oldpass", "network-portfrom"]:
                pass
            else:
                responses[k] = "unknown"
        return json.dumps(responses)
            
    def verify_conf_value(self, key, value):
        if key == "pyrt-oldpass":
            if self.Login.checkPassword(value):
                return "RESPONSE/OK/OK"
            else:
                currpass = self.Config.get("password")
                salt = base64.b64decode(currpass.split("$")[1])
                return "RESPONSE/NO/Incorrect Password"
        elif key in ["pyrt-refreshrate", "throttle-up", "throttle-down", "network-simuluploads",
                     "network-simuldownloads","network-maxpeers","network-maxpeersseed",
                     "network-maxopensockets","network-maxopenhttp","performance-maxmemory",
                     "performance-maxfilesize","performance-maxopenfiles",
                     "performance-receivebuffer","performance-sendbuffer",
                     "performance-readahead","general-stopat"]:
            try:
                test = int(value)
                return "RESPONSE/OK/OK"
            except ValueError:
                return "RESPONSE/NO/Value must be an integer"
        elif key == "pyrt-port":
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
            self.Log.error("AJAX: torrent pause error (ID: %s)", torrent_id)
            logging.error("%s %s","AJAX error - torrent could not be paused", traceback.format_exc())
            return "ERROR"
        else:
            self.Log.info("AJAX: torrent paused (ID: %s)", torrent_id)
            return "OK"
    
    def stop_torrent(self, torrent_id):
        try:
            self.RT.stop(torrent_id)
        except:
            self.Log.error("AJAX: torrent stop error (ID: %s)", torrent_id)
            logging.error("%s %s", "AJAX error - torrent could not be stopped", traceback.format_exc())
            return "ERROR"
        else:
            self.Log.info("AJAX: torrent stopped (ID: %s)", torrent_id)
            return "OK"
        
    def start_torrent(self, torrent_id):
        try:
            self.RT.resume(torrent_id)
        except:
            self.Log.error("AJAX: torrent resume error (ID: %s)", torrent_id)
            logging.error("%s %s", "AJAX error - torrent could not be resumed", traceback.format_exc())
            return "ERROR"
        else:
            self.Log.info("AJAX: torrent resumed (ID: %s)", torrent_id)
            return "OK"
        
    def remove_torrent(self, torrent_id):
        try:
            self.RT.remove(torrent_id)
        except:
            self.Log.error("AJAX: torrent remove error (ID: %s)", torrent_id)
            logging.error("%s %s", "AJAX error - torrent could not be removed", traceback.format_exc())
            return "ERROR"
        else:
            self.Log.info("AJAX: torrent removed (ID: %s)", torrent_id)
            return "OK"

    def hash_torrent(self, torrent_id):
        try:
            self.RT.rehash(torrent_id)
        except:
            self.Log.error("AJAX: torrent rehash error (ID: %s)", torrent_id)
            logging.error("%s %s", "AJAX error - torrent could not be rehashed", traceback.format_exc())
            return "ERROR"
        else:
            self.Log.info("AJAX: torrent rehash started (ID: %s)", torrent_id)
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
                self.Log.error("AJAX: torrent delete error - no such file '%s' (ID: %s)", delete, torrent_id)
                return "ERROR/no such file"
            else:
                try:
                    if os.path.isfile(delete):
                        os.remove(delete)
                    else:
                        shutil.rmtree(delete)
                    self.Log.info("AJAX: torrent deleted (ID: %s)", torrent_id)
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
    
    def load_from_remote(self, filename, remotename, start=True):
        """Loads a torrent from a file that has been fetched by a remote method"""
        self.Log.debug("File load request from remote handler %s (filename %s)", remotename, filename)
        if start:
            self.RT.start_from_file(os.path.join(os.getcwd(), "torrents/%s" % filename))
        else:
            self.RT.load_from_file(os.path.join(os.getcwd(), "torrents/%s" % filename))
        self.Log.info("AJAX: '%s' (downloaded via remote '%s') loaded%s successfully", filename, remotename, (start and " and started" or ""))
        return "OK"
        

    def upload_torrent_socket(self, torrent, start=True):
        fileName = torrent["filename"]
        inFile = torrent["content"]
        try:
            decoded = bencode.bdecode(inFile)
        except:
            self.Log.error("AJAX: '%s' (uploaded through fileSocket) is not a valid torrent file", fileName)
            return "ERROR/Invalid torrent file"
        else:
            newFile = open("torrents/%s" % (fileName), "wb")
            newFile.write(inFile)
            newFile.close()
            if start:
                self.RT.start_from_file(os.path.join(os.getcwd(), "torrents/%s" % fileName))
            else:
                self.RT.load_from_file(os.path.join(os.getcwd(), "torrents/%s" % fileName))
            self.Log.info("AJAX: '%s' (uploaded through fileSocket) loaded%s successfully", fileName, (start and " and started" or ""))
            return "OK"
        
    def upload_torrent(self, torrent=None, start=None):
        if type(torrent) is list:
            torrent = torrent[0]
        fileName = unicode(torrent["filename"])
        inFile = torrent["body"]
        try:
            decoded = bencode.bdecode(inFile)
        except:
            #Invalid torrent
            self.Log.error("AJAX: '%s' (uploaded via /ajax) is not a valid torrent file", fileName)
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
            self.Log.info("AJAX: '%s' (uploaded via /ajax) loaded%s successfully", fileName, (start and " and started" or ""))
            return self.Handler.HTMLredirect("/")
            
    def get_info_multi(self, view, sortby=None, reverse=None, drop_down_ids=None):
        drop_downs = {}
        if drop_down_ids:
            if not isinstance(drop_down_ids, list):
                drop_down_ids = drop_down_ids.split(",")
            elif "," in drop_down_ids[0]:
                drop_down_ids = drop_down_ids[0].split(",")
            for t_id in drop_down_ids:
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
        respList = []
        for torrent_id in torrentList:
            r = self.start_torrent(torrent_id)
            respList.append(r)
        return json.dumps(respList)
            
    def pause_batch(self, torrentListStr):
        torrentList = torrentListStr.split(",")
        respList = []
        for torrent_id in torrentList:
            respList.append(self.pause_torrent(torrent_id))
        return json.dumps(respList)
            
    def stop_batch(self, torrentListStr):
        torrentList = torrentListStr.split(",")
        respList = []
        for torrent_id in torrentList:
            respList.append(self.stop_torrent(torrent_id))
        return json.dumps(respList)
            
    def remove_batch(self, torrentListStr):
        torrentList = torrentListStr.split(",")
        respList = []
        for torrent_id in torrentList:
            respList.append(self.remove_torrent(torrent_id))
        return json.dumps(respList)
            
    def delete_batch(self, torrentListStr):
        torrentList = torrentListStr.split(",")
        respList = []
        for torrent_id in torrentList:
            respList.append(self.delete_torrent(torrent_id))
        return json.dumps(respList)

    def get_tracker_favicon(self, torrent_id):
        tracker_urls = [urlparse.urlparse(x.url) for x in self.RT.getTrackers(torrent_id)]
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
