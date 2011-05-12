#/usr/bin/env python

class Handler:
    """
        handler class for various reusable sundry operations
    """
    def __init__(self):
        pass

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
        """
        self.methods = ["name","size","ratio","uprate","uptotal","downrate","downtotal",
                        "leechs","leechs_connected","leechs_total","seeds",
                        "seeds_connected","seeds_total", "peers","peers_connected",
                        "peers_total","priority","status"]
        if sort not in ["name","size","ratio","uprate","uptotal","downrate","downtotal",
                        "leechs","leechs_connected","leechs_total","seeds",
                        "seeds_connected","seeds_total", "peers","peers_connected",
                        "peers_total","priority","status"]:
            sort = "name"

        if sort == "name":
            torrentList = sorted(torrentList, key=lambda x:x.name)
        elif sort == "size":
            torrentList = sorted(torrentList, key=lambda x:x.size)
        elif sort == "ratio":
            torrentList = sorted(torrentList, key=lambda x:x.ratio)
        elif sort == "uprate":
            torrentList = sorted(torrentList, key=lambda x:x.up_rate)
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

        torrent_html = """
            <table id='torrent_list'>
                <tr>
                    <td class='heading'>Name <img src='http://bits.wikimedia.org/skins-1.17/common/images/sort_up.gif'></td>
                    <td class='heading'>Size <img src='http://bits.wikimedia.org/skins-1.17/common/images/sort_none.gif'></td>
                    <td class='heading'>Ratio <img src='http://bits.wikimedia.org/skins-1.17/common/images/sort_none.gif'></td>
                    <td class='heading'>Upload speed <img src='http://bits.wikimedia.org/skins-1.17/common/images/sort_none.gif'></td>
                    <td class='heading'>Download speed <img src='http://bits.wikimedia.org/skins-1.17/common/images/sort_none.gif'></td>
                </tr>
            """
        div_colour_array = ["blue", "green"]
        for t in torrentList:
            colour = div_colour_array.pop(0)
            div_colour_array += [colour]
            torrent_html += """
                <tr onmouseover='select_torrent(this);' 
                    onmouseout='deselect_torrent(this);' 
                    onclick='view_torrent(this);' 
                    class='torrent-div %(colour)s' 
                    id='torrent_id_%(t_id)s'>
                    <td>%(t_name)s</td>
                    <td>%(t_size)s MiB</td>
                    <td title='%(t_uploaded).02f up / %(t_downloaded).02f down'>%(t_ratio).02f</td>
                    <td>%(t_uprate)s KB/s</td><td>%(t_downrate)s KB/s</td>
                </tr>""" % {
                            "colour" : colour,
                            "t_id" : t.torrent_id,
                            "t_name" : t.name,
                            "t_size" : int(float(t.size)/1024/1024),
                            "t_uploaded" : float(t.up_total)/1024/1024,
                            "t_downloaded" : float(t.down_total)/1024/1024,
                            "t_ratio" : float(t.ratio)/1000,
                            "t_uprate" : int(float(t.up_rate)/1024),
                            "t_downrate" : int(float(t.down_rate)/1024),
                        }
        torrent_html += "           </table>"

        html = """Content-Type: text/html\n\n
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
    <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
            <title>rTorrent - webUI</title>
            <link rel="stylesheet" type="text/css" href="css/main.css">
            <script src="javascript/main.js" type="text/javascript"></script>
        </head>
        <body>
            %s
        </body>
    </html>
        """ % torrent_html 
        return html
