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

import random
import string
import os
import re
import system
from modules.Cheetah.Template import Template

class Handler:
    """
        handler class for various reusable sundry operations
    """
    def __init__(self):
        self.SORT_METHODS = ["name","size","ratio","uprate","uptotal","downrate","downtotal",
                        "leechs","leechs_connected","leechs_total","seeds",
                        "seeds_connected","seeds_total", "peers","peers_connected",
                        "peers_total","priority","status", "tracker","created"]

    def humanTimeDiff(self, secs):
        time_str = ""
        if secs > 60*60*24*7:
            wks = secs / (60 * 60 * 24 * 7)
            time_str += "%iw " % wks
            secs -= wks * (60*60*24*7)
        if secs > 60*60*24:
            dys = secs / (60 * 60 * 24)
            time_str += "%id " % dys
            secs -= dys * (60 * 60 * 24)
        hrs = secs / (60*60)
        secs -= hrs * (60 * 60)
        mins = secs / 60
        secs -= mins * 60
        
        time_str += "%02ih %02i:%02i" % (hrs, mins, secs)
        
        return time_str
        
    def humanSize(self, bytes):
        """
            takes a int/float value of <bytes>
            returns a string of <bytes> in a human readable unit (with two decimal places)
            (currently supports TB, GB, MB, KB and B)
        """
        if bytes >= 1024*1024*1024*1024:
            return "%.02f TB" % (float(bytes) / 1024 / 1024 / 1024 / 1024)
        elif bytes >= 1024*1024*1024:
            return "%.02f GB" % (float(bytes) / 1024 / 1024 / 1024)
        elif bytes >= 1024*1024:
            return "%.02f MB" % (float(bytes) / 1024 / 1024)
        elif bytes >= 1024:
            return "%.02f KB" % (float(bytes) / 1024)
        else:
            return "%i B" % bytes

    def getState(self, t):
        """
            outputs a more 'advanced' status from an inputted <t> (rtorrent.Torrent object)
            possible outcomes:
                'Stopped'         # torrent is closed
                'Paused'          # torrent is open but inactive
                'Seeding (idle)'  # torrent is active and complete, but no connected peers
                'Seeding'         # torrent is active, complete, and has connected peers
                'Leeching (idle)' # torrent is active and incomplete, but no connected peers
                'Leeching'        # torrent is active, incomplete, and has connected peers
        """
        status_actual = t.status
        if status_actual == "Active":
            if t.completed_bytes == t.size:
                status = "Seeding"
                if t.peers_connected == 0:
                    status = "Seeding (idle)"
            else:
                status = "Leeching"
                if t.seeds_connected == 0 and t.peers_connected == 0:
                    status = "Leeching (idle)"
        else:
            status = t.status
        return status
    
    def HTMLredirect(self, url, refresh=0, body=""):
        return """
        <!DOCTYPE HTML>
        <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
                <meta http-equiv="REFRESH" content="%i;url=%s">
                <link rel="stylesheet" type="text/css" href="/css/main.css"
                <title>Redirect</title>
            </head>
            <body>
                %s
            </body>
        </html>
        """ % (refresh, url, body)
    
    def getFileStructure(self, files, rtorrent_root):
        folder = {}
        files_dict = {}
        priorites = {"high" : 2, "normal" : 1, "off" : 0}
        for file in files:
            random_id = "".join([random.choice(string.letters + string.digits) for i in range(10)])
            files_dict[random_id] = file
            if file.base_path == rtorrent_root:
                folder["."] = {"___files" : [random_id]}
                break
            else:
                if os.path.basename(file.base_path) not in folder.keys():
                    #create folder entry
                    folder[os.path.basename(file.base_path)] = {
                        "___files" : [],
                        "___size" : 0,
                        "___priority" : [file.priority],
                        "___completion" : 0,
                    }
                    
                for index in range(len(file.path_components)):
                    base = os.path.basename(file.base_path)
                    component = file.path_components[index]
                    if (index + 1) == len(file.path_components):
                        #it's a file
                        #last elem
                        #create entry
                        branch = folder[base]
                        rec_index = 0
                        while rec_index < index:
                            branch["___size"] += file.size
                            if file.priority not in branch["___priority"]:
                                branch["___priority"] += [file.priority]
                            branch["___completion"] = int((float(branch["___completion"]) + file.percentage_complete) / 2)
                            branch = branch[file.path_components[rec_index]]
                            rec_index += 1
                        branch["___files"] += [random_id]
                        branch["___size"] += file.size
                        if file.priority not in branch["___priority"]:
                            branch["___priority"] += [file.priority]
                        branch["___completion"] = int((float(branch["___completion"]) + file.percentage_complete) / 2)
                    else:
                        #it's a dir
                        #count index up
                        rec_index = 0
                        branch = folder[base]
                        while rec_index <= index:
                            if file.path_components[rec_index] not in branch.keys():
                                #create folder entry
                                branch[file.path_components[rec_index]] = {
                                    "___files" : [],
                                    "___size" : 0,
                                    "___priority" : [],
                                    "___completion" : 0,
                                }
                            branch = branch[file.path_components[rec_index]]
                            rec_index += 1
                            
        return (folder, files_dict)

    def fileTreeHTML(self, fileList, RTROOT):
        """
            Takes a list of files as outputted by rtorrent.getFiles and parses it into an html file tree
            Requires the rtorrent root directory
            File attributes:
                abs_path, base_path, path_components, completed_chunks, priority, size, chunks, chunk_size, percentage_complete
        """

        DOCUMENT_DIV = """
            <li><span class="file %s">%s<span class="fullpath">%s</span><span class="download%s">TEST TEST</span></span></li>
        """

        DIRECTORY_DIV = """
            <li><span class="folder">%s</span><ul>
        """
        
        def _getFiles(level):
            html = ""
            files = sorted(level["___files"], key=lambda x:os.path.basename(fileDict[x].abs_path))
            
            for file in files:
                # html += DOCUMENT_DIV % (HIDDEN, os.path.basename(fileDict[file].abs_path), self.humanSize(fileDict[file].size))
                fileName = os.path.basename(fileDict[file].abs_path)
                fileProgress = fileDict[file].percentage_complete
                if fileProgress == 100:
                    allowed = " allowed"
                else:
                    allowed = ""
                    
                html += DOCUMENT_DIV % (_getFileType(fileName), fileName, fileDict[file].abs_path, allowed)
            return html
            
        def _getDirs(level):
            level_keys = []
            for _key in level.keys():
                if _key[0:3] != "___":
                    level_keys += [_key]
            level_keys.sort()
            html = ""
            for subDirName in level_keys:
                subLevel = level[subDirName]
                # html += DIRECTORY_DIV % (HIDDEN, subDirName, self.humanSize(subLevel["___size"]))
                html += DIRECTORY_DIV % (subDirName)
                html += _getDirs(subLevel)
                html += _getFiles(subLevel)
                html += "</ul></li>"
            return html
            
        def _getFileType(fileName):
            fileType = "file_unknown"
            if fileName.lower().endswith(".avi") or fileName.lower().endswith(".mkv"):
                fileType = "file_video"
            elif fileName.lower().endswith(".rar"):
                fileType = "file_archive"
            elif "." in fileName and re.match("r\d+", fileName.lower().split(".")[-1]):
                fileType = "file_archive"
            elif fileName.lower().endswith(".nfo") or fileName.lower().endswith(".txt"):
                fileType = "file_document"
            elif fileName.lower().endswith(".iso"):
                fileType = "file_disk"
            elif "." in fileName and fileName.lower().split(".")[-1] in ["mp3", "aac", "flac", "m4a", "ogg"]:
                fileType = "file_music"
            return fileType
                
        fileStruct, fileDict = self.getFileStructure(fileList, RTROOT)
        root_keys = fileStruct.keys()
        root_keys.sort()
        if root_keys[0] == ".":
            fileObj = fileDict[fileStruct["."]["___files"][0]]
            fileName = os.path.basename(fileObj.abs_path)
            fileProgress = fileObj.percentage_complete
            if fileProgress == 100:
                # insert download icon
                allowed = " allowed"
            else:
                allowed = ""
            return """
                <ul id="files_list" class="filetree">
                    %s
                </ul>
                """ % (DOCUMENT_DIV % (_getFileType(fileName), fileName, fileObj.abs_path, allowed))
                # % (DOCUMENT_DIV % ("", os.path.basename(fileObj.abs_path), self.humanSize(fileObj.size)))
        else:
            #walk through dictionary
            #should only ever be one root_key, "." or the base directory
            html = "<ul class=\"filetree\">"
            root = fileStruct[root_keys[0]]
            #html += DIRECTORY_DIV % ("", root_keys[0], self.humanSize(root["___size"]))
            html += DIRECTORY_DIV % (root_keys[0])
            html += _getDirs(root)
            html += _getFiles(root)
            html += "</ul></li></ul>"
            return html
        
    def sortTorrents(self, torrentList, sort=None, reverse=False):
        if sort not in self.SORT_METHODS:
            sort = None

        if not sort:
            torrentList.reverse()
        elif sort == "name":
            torrentList = sorted(torrentList, key=lambda x:x.name)
        elif sort == "size":
            torrentList = sorted(torrentList, key=lambda x:x.size)
        elif sort == "ratio":
            torrentList = sorted(torrentList, key=lambda x:x.ratio)
        elif sort == "uprate":
            torrentList = sorted(torrentList, key=lambda x:x.up_rate)
            torrentList.reverse()
        elif sort == "downrate":
            torrentList = sorted(torrentList, key=lambda x:x.down_rate)
        elif sort == "uptotal":
            torrentList = sorted(torrentList, key=lambda x:x.up_total)
        elif sort == "downtotal":
            torrentList = sorted(torrentList, key=lambda x:x.down_total)
        elif sort == "leechs" or sort == "leechs_connected":
            torrentList = sorted(torrentList, key=lambda x:x.peers_connected)
        elif sort == "leechs_total":
            torrentList = sorted(torrentList, key=lambda x:x.peers_total)
        elif sort == "seeds" or sort == "seeds_connected":
            torrentList = sorted(torrentList, key=lambda x:x.seeds_connected)
        elif sort == "seeds_total":
            torrentList = sorted(torrentList, key=lambda x:x.seeds_total)
        elif sort == "peers" or sort == "peers_connected":
            torrentList = sorted(torrentList, key=lambda x:x.peers_connected + x.seeds_connected)
        elif sort == "peers_total":
            torrentList = sorted(torrentList, key=lambda x:x.peers_total + x.seeds_total)
        elif sort == "priority":
            torrentList = sorted(torrentList, key=lambda x:x.priority)
        elif sort == "status":
            torrentList = sorted(torrentList, key=lambda x:x.status)
        elif sort == "tracker":
            #sort by the first listed tracker only
            torrentList = sorted(torrentList, key=lambda x:x.trackers[0].url)
        elif sort == "created":
            torrentList = sorted(torrentList, key=lambda x:x.created)
      
        if reverse:
            torrentList.reverse()
            
        return torrentList
        
    def torrentHTML(self, torrentList, sort, view, reverse=None):
        """
            Sorts a list of torrent_ids with default information
            Arguments:
                torrentList = list : rtorrent.Torrent objects
                sort = str : value to sort on
                reverse = boolean : reverse or not
            Sort Options:
                name, size, ratio, uprate, uptotal,
                downrate, downtotal, leechs, leechs_connected,
                leechs_total, seeds, seeds_connected,
                seeds_total, peers, peers_connected,
                peers_total, priority, status, tracker, created
                
                leechs, seeds, and peers are shorthand for leechs_connected, 
                seeds_connected and peers_connected respectively
        """
        
        torrentList = self.sortTorrents(torrentList, sort, reverse)
        updated_torrentList = []
        for t in torrentList:
            t.t_size = self.humanSize(t.size)
            t.t_uploaded = self.humanSize(t.up_total)
            t.t_downloaded = self.humanSize(t.down_total)
            t.t_ratio = "%.02f" % (float(t.ratio)/1000)
            t.t_uprate = self.humanSize(t.up_rate)
            t.t_downrate = self.humanSize(t.down_rate)
            t.t_percentage = int((float(t.completed_bytes) / t.size) * 100)
            updated_torrentList += [t]
        
        searchList = [{
            "global" : system.get_global(),
            "torrent_list" : updated_torrentList,
            "this_view" : view,
            "this_sort" : sort,
            "this_reverse" : reverse,
            "self" : self,
            
        }]
        
        HTML = Template(file="htdocs/torrentHTML.tmpl", searchList=searchList).respond()
        return HTML
