#!/usr/bin/env python

import random
import string
import os

class Handler:
    """
        handler class for various reusable sundry operations
    """
    def __init__(self):
        pass

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
        if bytes > 1024*1024*1024*1024:
            return "%.02f TB" % (float(bytes) / 1024 / 1024 / 1024)
        elif bytes > 1024*1024*1024:
            return "%.02f GB" % (float(bytes) / 1024 / 1024 / 1024)
        elif bytes > 1024*1024:
            return "%.02f MB" % (float(bytes) / 1024 / 1024)
        elif bytes > 1024:
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
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
        <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
                <meta http-equiv="REFRESH" content="%i;url=%s">
                <title>Redirect</title>
            </head>
            <body>
                %s
            </body>
        </html>
        """ % (url, refresh, body)
        
    def getFileStructure(self, files, rtorrent_root):
        """
            Takes a list of <files> (as outputted by rtorrent.getFiles) and converts it into a file structure
            Returns a tuple of two dictionaries
                ( files , files_dict )
            Files contains the file hierachy (two levels maximum) with file_id strings
            Files_dict contains the original rtorrent.File instances indexed by their file_id strings
        """
        folder = {}
        files_dict = {}
        priority_lookup = {"high" : 2, "normal" : 1, "off" : 0}
        for file in files:
            random_id = "".join([random.choice(string.letters + string.digits) for i in range(10)])
            files_dict[random_id] = file
            if file.base_path == rtorrent_root:
                folder["."] = {"_files" : [random_id]}
            else:
                if len(file.path_components) == 1:
                    if os.path.basename(file.base_path) not in folder.keys():
                        folder[os.path.basename(file.base_path)] = {"_files" : [random_id], "_size" : file.size, "_priority" : [file.priority], "_completion" : file.percentage_complete}
                    else:
                        folder[os.path.basename(file.base_path)]["_files"] += [random_id]
                        folder[os.path.basename(file.base_path)]["_size"] += file.size
                        if file.priority not in folder[os.path.basename(file.base_path)]["_priority"]:
                            folder[os.path.basename(file.base_path)]["_priority"] += [file.priority]
                        prev = folder[os.path.basename(file.base_path)]["_completion"]
                        new = (prev + file.percentage_complete) / 2
                        folder[os.path.basename(file.base_path)]["_completion"] = new
                else:
                    if os.path.basename(file.base_path) not in folder.keys():
                        folder[os.path.basename(file.base_path)] = {file.path_components[0] : {"_files" : [random_id], "_size" : file.size, "_priority" : [file.priority], "_completion" : file.percentage_complete}}
                    else:
                        if file.path_components[0] not in folder[os.path.basename(file.base_path)].keys():
                            folder[os.path.basename(file.base_path)][file.path_components[0]] = {"_files" : [random_id], "_size" : file.size, "_priority" : [file.priority], "_completion" : file.percentage_complete}
                        else:
                            folder[os.path.basename(file.base_path)][file.path_components[0]]["_files"] += [random_id]
                            folder[os.path.basename(file.base_path)][file.path_components[0]]["_size"] += file.size
                            if file.priority not in folder[os.path.basename(file.base_path)][file.path_components[0]]["_priority"]:
                                folder[os.path.basename(file.base_path)][file.path_components[0]]["_priority"] += [file.priority]
                            folder[os.path.basename(file.base_path)][file.path_components[0]]["_completion"] = (folder[os.path.basename(file.base_path)][file.path_components[0]]["_completion"] + file.percentage_complete) / 2
        return (folder, files_dict)
        
    def torrentHTML(self, torrentList, sort, view, reverse=False):
        """
            Sorts a list of torrent_ids with default information
            Arguments:
                torrentList = list : rtorrent.Torrent objects
                sort = str : value to sort on
                reverse = boolean : reverse or not
            Sort Options:
                name
                size
                ratio
                uprate
                uptotal
                downrate
                downtotal
                leechs              #shorthand for leechs_connected
                leechs_connected
                leechs_total
                seeds               #shorthand for seeds_connected
                seeds_connected
                seeds_total
                peers               #shorthand for peers_connected
                peers_connected
                peers_total
                priority
                status
                tracker
                created
        """
        self.SORT_METHODS = ["name","size","ratio","uprate","uptotal","downrate","downtotal",
                        "leechs","leechs_connected","leechs_total","seeds",
                        "seeds_connected","seeds_total", "peers","peers_connected",
                        "peers_total","priority","status", "tracker","created"]
        if sort not in ["name","size","ratio","uprate","uptotal","downrate","downtotal",
                        "leechs","leechs_connected","leechs_total","seeds",
                        "seeds_connected","seeds_total", "peers","peers_connected",
                        "peers_total","priority","status","tracker","created"]:
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

        sorts = {
            "name":"",
            "namesort" : "none",
            "size":"",
            "sizesort" : "none",
            "ratio":"",
            "ratiosort" : "none",
            "uprate" : "",
            "upratesort" : "none",
            "downrate" : "",
            "downratesort" : "none",
            "status" : "",
            "statussort" : "none",
        }
        for type in sorts.keys():
            if type in self.SORT_METHODS:
                sorts[type] = "?view=%s&sortby=%s" % (view, type)
                if type == sort and not reverse:
                    sorts[type] += "&reverse=1"
        if sort in sorts.keys():
            if reverse:
                sorts[sort + "sort"] = "down"
            else:
                sorts[sort + "sort"] = "up"
                    
        
        torrent_html = """
            <table id='torrent_list'>
                <tr>
                    <td class='heading' id="sortby_name" onclick="window.location='%(name)s';">Name <img alt="Sort By Name" src="../images/sort_%(namesort)s.gif" class="control_button"></td>
                    <td class='heading' id="sortby_size" onclick="window.location='%(size)s';">Size <img alt="Sort By Size" src="../images/sort_%(sizesort)s.gif" class="control_button"></td>
                    <td class='heading' id="sortby_ratio" onclick="window.location='%(ratio)s';">Ratio <img alt="Sort By Ratio" src="../images/sort_%(ratiosort)s.gif" class="control_button"></td>
                    <td class='heading' id="sortby_uprate" onclick="window.location='%(uprate)s';">Upload speed <img alt="Sort By Upload Speed" src="../images/sort_%(upratesort)s.gif" class="control_button"></td>
                    <td class='heading' id="sortby_downrate" onclick="window.location='%(downrate)s';">Download speed <img alt="Sort By Download Speed" src="../images/sort_%(downratesort)s.gif" class="control_button"></td>
                    <td class='heading' id="sortby_status" onclick="window.location='%(status)s';">Status <img alt="Sort By Status" src="../images/sort_%(statussort)s.gif" class="control_button"></td>
                    <td class='heading'></td>
                </tr>
            """ % sorts
        torrent_html += "<!-- %r -->" % sorts
            
        div_colour_array = ["blue", "green"]
        for t in torrentList:
            colour = div_colour_array.pop(0)
            div_colour_array += [colour]
            status = self.getState(t)
            if status == "Stopped" or status == "Paused":
                stopstart = "<span id='control_start' class='control_button' title='Start Torrent'><img onclick='event.cancelBubble = true; command(\"start_torrent\",\"%s\")' class='control_image' alt='Start' src='../images/start.png'></span>" % t.torrent_id
            else:
                stopstart = "<span id='control_pause' class='control_button' title='Pause Torrent'><img onclick='event.cancelBubble = true; command(\"pause_torrent\",\"%s\")'class='control_image' alt='Pause' src='../images/pause.png'></span>" % t.torrent_id
            torrent_html += """
                <tr onmouseover='select_torrent(this);' 
                    onmouseout='deselect_torrent(this);' 
                    onclick='view_torrent(this);'
                    ondblclick='navigate_torrent(this);'
                    class='torrent-div %(colour)s' 
                    id='torrent_id_%(t_id)s'>
                    <td>%(t_name)s</td>
                    <td>%(t_size)s</td>
                    <td title='%(t_uploaded)s up / %(t_downloaded)s down'>%(t_ratio).02f</td>
                    <td>%(t_uprate)s/s</td>
                    <td>%(t_downrate)s/s</td>
                    <td>%(t_status)s</td>
                    <td>
                        %(control_startpause)s
                        <span id='control_stop' class='control_button' title='Stop Torrent'>
                            <img onclick='event.cancelBubble = true; command(\"stop_torrent\",\"%(t_id)s\")'
                                 class='control_image' alt='Stop' src='../images/stop.png'>
                        </span>
                        <span id='control_remove' class='control_button' title='Remove Torrent'>
                            <img onclick='event.cancelBubble = true; command(\"remove_torrent\",\"%(t_id)s\")'
                                 class='control_image' alt='Remove' src='../images/remove.png'>
                        </span>
                        <span id='control_delete' class='control_button' title='Remove Torrent and Files'>
                            <img onclick='event.cancelBubble = true; command(\"delete_torrent\",\"%(t_id)s\")'
                                 class='control_image' alt='Delete' src='../images/delete.png'>
                        </span>
                    </td>
                </tr>
                        """ % {
                            "colour" : colour,
                            "t_id" : t.torrent_id,
                            "t_name" : t.name,
                            "t_size" : self.humanSize(t.size),
                            "t_uploaded" : self.humanSize(t.up_total),
                            "t_downloaded" : self.humanSize(t.down_total),
                            "t_ratio" : float(t.ratio)/1000,
                            "t_uprate" : self.humanSize(t.up_rate),
                            "t_downrate" : self.humanSize(t.down_rate),
                            "t_status" : status,
                            "control_startpause" : stopstart,
                        }
        torrent_html += "\n             </table>"

        html = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
    <head>
        <!-- HEAD PLACEHOLDER -->
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
        <title>rTorrent - webUI</title>
        <link rel="stylesheet" type="text/css" href="../css/main.css">
        <script src="../javascript/main.js" type="text/javascript"></script>
    </head>
    <body>
        <!-- BODY PLACEHOLDER -->
        <div id="torrent_table">
            %s
        </div>
    </body>
</html>
        """ % torrent_html 
        return html
