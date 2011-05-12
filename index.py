#!/usr/bin/env python

import cgi
import os
import sys
import rtorrent
import cgitb
cgitb.enable()

RT = rtorrent.rtorrent(5000)
torrentList = RT.getTorrentList()

torrent_html = "<table id='torrent_list'><tr><td class='heading'>Name</td><td class='heading'>Size</td>"
torrent_html += "<td class='heading'>Ratio</td><td class='heading'>Upload speed</td>"
torrent_html += "<td class='heading'>Download speed</td></tr>"
div_colour_array = ["blue", "green"]
for t_id, t_name in torrentList.iteritems():
    colour = div_colour_array.pop(0)
    div_colour_array += [colour]
    if RT.conn.d.get_peers_connected(t_id) > 0:
        colour = "red"
    torrent_html += "<tr onmouseover='select_torrent(this);' onmouseout='deselect_torrent(this);' onclick='view_torrent(this);' class='torrent-div %s' id='torrent_id_%s'>" % (colour, t_id)
    torrent_html += "<td>%s</td><td>%i MiB</td>" % (t_name, int(float(RT.getSizeBytes(t_id))/1024/1024))
    torrent_html += "<td title='%.02f up / %.02f down'>%.02f</td>" % (float(RT.getUploadBytes(t_id))/1024/1024, float(RT.getDownloadBytes(t_id))/1024/1024, float(RT.getRatio(t_id))/1000 )
    torrent_html += "<td>%s KB/s</td><td>%s KB/s</td>" % (int(float(RT.getUploadSpeed(t_id))/1024), int(float(RT.getDownloadSpeed(t_id))/1024))
    torrent_html += "</tr>"
torrent_html += "</table>"
print """Content-Type:text/html\n\n
Hi!
"""
if False:
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
