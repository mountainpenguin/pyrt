#!/usr/bin/env python

import cgi
import os
import sys
import rtorrent
import cgitb
cgitb.enable()

RT = rtorrent.rtorrent(5000)
torrentList = RT.getTorrentList()

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
for t_id, t_name in torrentList.iteritems():
    colour = div_colour_array.pop(0)
    div_colour_array += [colour]
    if RT.conn.d.get_peers_connected(t_id) > 0:
        colour = "red"
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
                            "t_id" : t_id,
                            "t_name" : t_name,
                            "t_size" : int(float(RT.getSizeBytes(t_id))/1024/1024),
                            "t_uploaded" : float(RT.getUploadBytes(t_id))/1024/1024,
                            "t_downloaded" : float(RT.getDownloadBytes(t_id))/1024/1024,
                            "t_ratio" : float(RT.getRatio(t_id))/1000,
                            "t_uprate" : int(float(RT.getUploadSpeed(t_id))/1024),
                            "t_downrate" : int(float(RT.getDownloadSpeed(t_id))/1024),
                        }
torrent_html += "           </table>"

print """Content-Type: text/html\n\n
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
