#/usr/bin/env python

class Handler:
    """
        handler class for various reusable sundry operations
    """
    def __init__(self):
        pass

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

    def torrentHTML(self, torrentList, sort, reverse=False):
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

        if sort == "name":
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

        torrent_html = """
            <table id='torrent_list'>
                <tr>
                    <td class='heading'>Name</td>
                    <td class='heading'>Size</td>
                    <td class='heading'>Ratio</td>
                    <td class='heading'>Upload speed</td>
                    <td class='heading'>Download speed</td>
                    <td class='heading'>Status</td>
                </tr>
            """
        div_colour_array = ["blue", "green"]
        for t in torrentList:
            colour = div_colour_array.pop(0)
            div_colour_array += [colour]
            status = self.getState(t)
                
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
                        }
        torrent_html += "\n             </table>"

        html = """Content-Type: text/html\n\n
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
