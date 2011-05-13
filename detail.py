#/usr/bin/env python

import cgi

import rtorrent
import random
import string
import os

def _humanSize(bytes):
    if bytes > 1024*1024*1024:
        return "%.02f GB" % (float(bytes) / 1024 / 1024 / 1024)
    elif bytes > 1024*1024:
        return "%.02f MB" % (float(bytes) / 1024 / 1024)
    elif bytes > 1024:
        return "%.02f KB" % (float(bytes) / 1024)
    else:
        return "%i B" % bytes

def main(torrent_id):
    trackers = RT.getTrackers(torrent_id)
    seeds = 0
    leechs = 0
    for tracker in trackers:
        seeds += tracker.seeds
        leechs += tracker.leechs
    info_dict = {
        "tname" : RT.getNameByID(torrent_id),
        "tid" : torrent_id,
        "tcreated" : RT.getCreationDate(torrent_id),
        "tpath" : RT.getPath(torrent_id),
        "tpriority" : RT.getPriorityStr(torrent_id),
        "tstate" : RT.getStateStr(torrent_id),
        "tsize" : _humanSize(RT.getSizeBytes(torrent_id)),
        "tratio" : "%.02f" % (float(RT.getRatio(torrent_id))/1000),
        "tuploaded" : _humanSize(RT.getUploadBytes(torrent_id)),
        "tdownloaded" : _humanSize(RT.getDownloadBytes(torrent_id)),
        "tdone" : "%.02f" % (100*(float(RT.conn.d.get_completed_bytes(torrent_id)) / RT.getSizeBytes(torrent_id))),
        "tuprate" : "%s/s" % _humanSize(RT.getUploadSpeed(torrent_id)),
        "tdownrate" : "%s/s" % _humanSize(RT.getDownloadSpeed(torrent_id)),
        "tseeds_connected" : RT.conn.d.get_peers_complete(torrent_id),
        "tseeds_total" : seeds,
        "tleechs_connected" : RT.conn.d.get_peers_accounted(torrent_id),
        "tleechs_total" : leechs,
    }
    print """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
        <title>rTorrent - %(tname)s</title>
        <link rel="stylesheet" type="text/css" href="css/main.css">
        <script src="javascript/detail.js" type="text/javascript"></script>
    </head>
    <body>
        <div id="topbar">
            <div class="topbar-tab_home" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate_home();" title="Home" id="home">Home</div>
            <div class="topbar-tab selected" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" id="info" title="Info">Info</div>
            <div class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="Peers" id="peers">Peers</div>
            <div class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="File List" id="files">File List</div>
            <div class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="Trackers" id="trackers">Tracker List</div>
        </div>
        <div id="main">
            <div class="column-1">Name:</div><div class="column-2">%(tname)s</div>
            <div class="column-1">ID:</div><div class="column-2">%(tid)s</div>
            <div class="column-1">Created:</div><div class="column-2">%(tcreated)s</div>
            <div class="column-1">Path:</div><div class="column-2">%(tpath)s</div>
            <div class="column-1">Priority:</div><div class="column-2">%(tpriority)s</div>
            <div class="column-1 %(tstate)s">State:</div><div class="column-2">%(tstate)s</div>
            <br>
            <div class="down-1"><div class="column-1">Total Size:</div><div class="column-2">%(tsize)s</div></div>
            <div class="column-1">Percentage:</div><div class="column-2">%(tdone)s%%</div>
            <div class="column-1">Ratio:</div><div class="column-2">%(tratio)s</div>
            <div class="column-1">Uploaded:</div><div class="column-2">%(tuploaded)s</div>
            <div class="column-1">Downloaded:</div><div class="column-2">%(tdownloaded)s</div>
            <br>
            <div class="down-1"><div class="column-1">Up Rate:</div><div class="column-2">%(tuprate)s</div></div>
            <div class="column-1">Down Rate:</div><div class="column-2">%(tdownrate)s</div>
           
            <div class="down-1"><div class="column-1">Leechers:</div><div class="column-2">%(tleechs_connected)s (%(tleechs_total)s)</div></div>
            <div class="column-1">Seeders:</div><div class="column-2">%(tseeds_connected)s (%(tseeds_total)s)</div>
        </div>
    </body>
</html>""" % info_dict

def peers(torrent_id):

    peer_html = "\n"
    colours = ["blue", "green"]
    for peer in RT.getPeers(torrent_id):
        colour = colours.pop(0)
        colours += [colour]
        peer.address = ".".join(peer.address.split(".")[:2]) + ".x.x"
        peer.down_rate = "%s/s" % _humanSize(peer.down_rate)
        peer.down_total = _humanSize(peer.down_total)
        peer.up_rate = "%s/s" % _humanSize(peer.up_rate)
        peer.up_total = _humanSize(peer.up_total)
        peer.peer_rate = "%s/s" % _humanSize(peer.peer_rate)
        peer.peer_total = _humanSize(peer.peer_total)
        peer_html += "\t\t\t\t\t<tr class='%s'>\n" % colour
        peer_html += "\t\t\t\t\t\t<td>%(address)s</td>\n" % peer.__dict__
        peer_html += "\t\t\t\t\t\t<td>%(port)s</td><td>%(client_version)s</td><td>%(completed_percent)s%%</td>\n" % peer.__dict__
        peer_html += "\t\t\t\t\t\t<td>%(down_rate)s</td><td>%(down_total)s</td>\n" % peer.__dict__
        peer_html += "\t\t\t\t\t\t<td>%(up_rate)s</td><td>%(up_total)s</td>\n" % peer.__dict__
        peer_html += "\t\t\t\t\t\t<td>%(peer_rate)s</td><td>%(peer_total)s</td>\n" % peer.__dict__
        peer_html += "\t\t\t\t\t</tr>\n\n"

    info_dict = {
        "tname" : RT.getNameByID(torrent_id),
        "tid" : torrent_id,
        "tcreated" : RT.getCreationDate(torrent_id),
        "tpath" : RT.getPath(torrent_id),
        "tpriority" : RT.getPriorityStr(torrent_id),
        "tstate" : RT.getStateStr(torrent_id),
        "peerhtml" : peer_html.replace("\t","    "),
    }
    print """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
        <title>rTorrent - %(tname)s</title>
        <link rel="stylesheet" type="text/css" href="css/main.css">
        <script src="javascript/detail.js" type="text/javascript"></script>
    </head>
    <body>
        <div id="topbar">
            <div class="topbar-tab_home" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate_home();" title="Home" id="home">Home</div>
            <div class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" id="info" title="Info">Info</div>
            <div class="topbar-tab selected" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="Peers" id="peers">Peers</div>
            <div class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="File List" id="files">File List</div>
            <div class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="Trackers" id="trackers">Tracker List</div>
        </div>
        <div id="main">
            <div class="column-1">Name:</div><div class="column-2">%(tname)s</div>
            <div class="column-1">ID:</div><div class="column-2">%(tid)s</div>
            <div class="column-1">Created:</div><div class="column-2">%(tcreated)s</div>
            <div class="column-1">Path:</div><div class="column-2">%(tpath)s</div>
            <div class="column-1">Priority:</div><div class="column-2">%(tpriority)s</div>
            <div class="column-1 %(tstate)s">State:</div><div class="column-2">%(tstate)s</div>
            <div id="peers_table">
                <table>
                    <tr>
                        <td class="heading">IP Address</td>
                        <td class="heading">Port</td>
                        <td class="heading">Client</td>
                        <td class="heading">Completed</td>
                        <td class="heading">Download Rate</td>
                        <td class="heading">Download Total</td>
                        <td class="heading">Upload Rate</td>
                        <td class="heading">Upload Total</td>
                        <td class="heading">Peer Rate</td>
                        <td class="heading">Peer Total</td>
                    </tr>
                    %(peerhtml)s
                </table>
            </div>
        </div>
    </body>
</html>""" % info_dict


def files(torrent_id):
    file_html = "\n"
    files = RT.getFiles(torrent_id)
    folder = {}
    files_dict = {}
    rtorrent_root = RT.getRootDir()
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
    folder_keys = folder.keys()
    folder_keys.sort()
    for folder_name in folder_keys:
        #folder_name : {"_files" : [file_id,...],
        #               folder_name : {"_files : [file_id,...],
        #                           }
        #               }
        if folder_name == ".":
            the_file = files_dict[folder[folder_name]["_files"][0]]
            file_html += "\t\t\t\t<div class='file level-1'>\n\t\t\t\t\t<span class='file_priority'>%s</span>\n\t\t\t\t\t<span class='file_completion'>%s%%</span>\n\t\t\t\t\t<span class='file_size'>%s</span>\n\t\t\t\t\t<span class='file_name'>%s</span>\n\t\t\t\t</div>\n" % (the_file.priority, int((float(the_file.completed_chunks) / the_file.chunks) * 100), _humanSize(the_file.size), os.path.basename(the_file.abs_path))

        else: #multiple folders
            folder_contents = folder[folder_name]
            if "_size" in folder_contents.keys():
                file_html += "\t\t\t\t<div class='folder level-1'>\n\t\t\t\t\t<div class='folder_name'>\n\t\t\t\t\t\t<span class='file_completion'>%s%%</span>\n\t\t\t\t\t\t<span class='file_size'>%s</span>\n\t\t\t\t\t\t<span class='file_name'>%s</span>\n\t\t\t\t\t</div>\n" % (int(folder_contents["_completion"]), _humanSize(folder_contents["_size"]), folder_name)

#~                file_html += "\t\t\t\t<div class='folder level-1'>\n\t\t\t\t\t<div class='folder_name'>\n\t\t\t\t\t\t<span class='file_priority'>%s</span>\n\t\t\t\t\t\t<span class='file_completion'>%s%%</span>\n\t\t\t\t\t\t<span class='file_size'>%s</span>\n\t\t\t\t\t\t<span class='file_name'>%s</span>\n\t\t\t\t\t</div>\n" % ("/".join(sorted(folder_contents["_priority"], key=lambda x : x)), int(folder_contents["_completion"]), _humanSize(folder_contents["_size"]), folder_name)
            else:
                file_html += "\t\t\t\t<div class='folder level-1'><div class='folder_name'>%s</div>\n" % folder_name
            folder_contents_keys_ = folder_contents.keys()
            folder_contents_keys = []
            for i in folder_contents_keys_:
                if i[0] == "_":
                    pass
                else:
                    folder_contents_keys += [i]
            folder_contents_keys.sort()
            for folder_name_sub in folder_contents_keys:
                if "_size" in folder[folder_name][folder_name_sub].keys():
                    file_html += "\t\t\t\t\t<div class='folder level-2'>\n\t\t\t\t\t\t<div class='folder_name'>\n\t\t\t\t\t\t\t<span class='file_completion'>%s%%</span>\n\t\t\t\t\t\t\t<span class='file_size'>%s</span>\n\t\t\t\t\t\t\t<span class='file_name'>%s</span>\n\t\t\t\t\t\t</div>\n" % (int(folder[folder_name][folder_name_sub]["_completion"]), _humanSize(folder[folder_name][folder_name_sub]["_size"]), folder_name_sub)

#~                    file_html += "\t\t\t\t\t<div class='folder level-2'>\n\t\t\t\t\t\t<div class='folder_name'>\n\t\t\t\t\t\t\t<span class='file_priority'>%s</span>\n\t\t\t\t\t\t\t<span class='file_completion'>%s%%</span>\n\t\t\t\t\t\t\t<span class='file_size'>%s</span>\n\t\t\t\t\t\t\t<span class='file_name'>%s</span>\n\t\t\t\t\t\t</div>\n" % ("/".join(sorted(folder[folder_name][folder_name_sub]["_priority"], key=lambda x:x)), int(folder[folder_name][folder_name_sub]["_completion"]), _humanSize(folder[folder_name][folder_name_sub]["_size"]), folder_name_sub)
   
                else:
                    file_html += "\t\t\t\t\t<div class='folder level-2'><div class='folder_name'>%s</div>\n" % folder_name_sub
                files_ = folder[folder_name][folder_name_sub]["_files"]
                files_ = sorted(files_, key=lambda x : "/".join(files_dict[x].path_components[1:]))
                for file in files_:
                    the_file = files_dict[file]
                    file_html += "\t\t\t\t\t\t<div class='file level-3'>\n\t\t\t\t\t\t\t<span class='file_priority'>%s</span>\n\t\t\t\t\t\t\t<span class='file_completion'>%s%%</span>\n\t\t\t\t\t\t\t<span class='file_size'>%s</span>\n\t\t\t\t\t\t\t<span class='file_name'>%s</span>\n\t\t\t\t\t\t</div>\n" % (the_file.priority, int((float(the_file.completed_chunks) / the_file.chunks) * 100), _humanSize(the_file.size), os.path.basename(the_file.abs_path))
                file_html += "\t\t\t\t\t</div>\n"
            if "_files" in folder_contents.keys():
                files_ = sorted(folder_contents["_files"], key=lambda x : files_dict[x].path_components[0])
                for file in files_:
                    the_file = files_dict[file]
                    file_html += "\t\t\t\t\t<div class='file level-2'>\n\t\t\t\t\t\t<span class='file_priority'>%s</span>\n\t\t\t\t\t\t<span class='file_completion'>%s%%</span>\n\t\t\t\t\t\t<span class='file_size'>%s</span>\n\t\t\t\t\t\t<span class='file_name'>%s</span>\n\t\t\t\t\t</div>\n" % (the_file.priority, int((float(the_file.completed_chunks) / the_file.chunks) * 100), _humanSize(the_file.size), os.path.basename(the_file.abs_path))
            file_html += "\t\t\t\t</div>" 
    
    info_dict = {
        "tname" : RT.getNameByID(torrent_id),
        "tid" : torrent_id,
        "tcreated" : RT.getCreationDate(torrent_id),
        "tpath" : RT.getPath(torrent_id),
        "tpriority" : RT.getPriorityStr(torrent_id),
        "tstate" : RT.getStateStr(torrent_id),
#~        "filehtml" : repr(folder)
#~        "filehtml" : "\n\t\t\t\t".join([repr(x.__dict__) for x in files]).replace("\t","    ")
        "filehtml" : file_html.replace("\t","    ")
    }
    print """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
        <title>rTorrent - %(tname)s</title>
        <link rel="stylesheet" type="text/css" href="css/main.css">
        <script src="javascript/detail.js" type="text/javascript"></script>
    </head>
    <body>
        <div id="topbar">
            <div class="topbar-tab_home" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate_home();" title="Home" id="home">Home</div>
            <div class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" id="info" title="Info">Info</div>
            <div class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="Peers" id="peers">Peers</div>
            <div class="topbar-tab selected" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="File List" id="files">File List</div>
            <div class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="Trackers" id="trackers">Tracker List</div>
        </div>
        <div id="main">
            <div class="column-1">Name:</div><div class="column-2">%(tname)s</div>
            <div class="column-1">ID:</div><div class="column-2">%(tid)s</div>
            <div class="column-1">Created:</div><div class="column-2">%(tcreated)s</div>
            <div class="column-1">Path:</div><div class="column-2">%(tpath)s</div>
            <div class="column-1">Priority:</div><div class="column-2">%(tpriority)s</div>
            <div class="column-1 %(tstate)s">State:</div><div class="column-2">%(tstate)s</div>
            <div id="files_div">
                %(filehtml)s
            </div>
        </div>
    </body>
</html>""" % info_dict

def trackers(torrent_id):
    tracker_html = "\n"
    colours = ["blue", "green"]
    trackers = RT.getTrackers(torrent_id)
    for tracker in trackers:
        colour = colours.pop(0)
        colours += [colour]
        tracker_html += "\t\t\t\t\t<tr class='%s'>\n" % colour
        tracker_html += "\t\t\t\t\t\t<td>%(url)s</td>\n\t\t\t\t\t\t<td>%(type)s</td>\n\t\t\t\t\t\t<td>%(interval)s</td>\n\t\t\t\t\t\t<td>%(seeds)s</td>\n\t\t\t\t\t\t<td>%(leechs)s</td>\n\t\t\t\t\t\t<td>%(enabled)s</td>" % (
            {
                "type" : {1:"HTTP",2:"UDP",3:"DHT"}[tracker.type],
                "url" : tracker.url.split("//")[0] + "//" + "***",
                #~"url" : tracker.url.split("//")[0] + "//" + tracker.url.split("//")[1].split("/")[0] + "/***"*len(tracker.url.split("//")[1].split("/")[1:]),
                "interval" : tracker.interval,
                "seeds" : tracker.seeds,
                "leechs" : tracker.leechs,
                "enabled" : tracker.enabled,
            }
        )
        tracker_html += "\t\t\t\t\t</tr>\n"

    info_dict = {
        "tname" : RT.getNameByID(torrent_id),
        "tid" : torrent_id,
        "tcreated" : RT.getCreationDate(torrent_id),
        "tpath" : RT.getPath(torrent_id),
        "tpriority" : RT.getPriorityStr(torrent_id),
        "tstate" : RT.getStateStr(torrent_id),
        "trackerhtml" : tracker_html.replace("\t","    "),
    }
    print """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
        <title>rTorrent - %(tname)s</title>
        <link rel="stylesheet" type="text/css" href="css/main.css">
        <script src="javascript/detail.js" type="text/javascript"></script>
    </head>
    <body>
        <div id="topbar">
            <div class="topbar-tab_home" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate_home();" title="Home" id="home">Home</div>
            <div class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" id="info" title="Info">Info</div>
            <div class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="Peers" id="peers">Peers</div>
            <div class="topbar-tab" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="File List" id="files">File List</div>
            <div class="topbar-tab selected" onmouseover="select(this);" onmouseout="deselect(this);" onclick="navigate(this);" title="Trackers" id="trackers">Tracker List</div>

        </div>
        <div id="main">
            <div class="column-1">Name:</div><div class="column-2">%(tname)s</div>
            <div class="column-1">ID:</div><div class="column-2">%(tid)s</div>
            <div class="column-1">Created:</div><div class="column-2">%(tcreated)s</div>
            <div class="column-1">Path:</div><div class="column-2">%(tpath)s</div>
            <div class="column-1">Priority:</div><div class="column-2">%(tpriority)s</div>
            <div class="column-1 %(tstate)s">State:</div><div class="column-2">%(tstate)s</div>
            <div id="peers_table">
                <table>
                    <tr>
                        <td class="heading">URL</td>
                        <td class="heading">Type</td>
                        <td class="heading">Announce Interval</td>
                        <td class="heading">Seeders</td>
                        <td class="heading">Leechers</td>
                        <td class="heading">Enabled</td>
                    </tr>
                    %(trackerhtml)s
                </table>
            </div>
        </div>
    </body>
</html>""" % info_dict

if __name__ == "__main__":
    RT = rtorrent.rtorrent("/home/torrent/.session/rpc.socket")
    form = cgi.FieldStorage()
    torrent_id = form.getfirst("torrent_id")
    view = form.getfirst("view")

    if not torrent_id:
        print "ERROR/Not Implemented"
    elif not view or view == "info":
        main(torrent_id)
    elif view == "peers":
        peers(torrent_id)
    elif view == "files":
        files(torrent_id)
    elif view == "trackers":
        trackers(torrent_id)
