#!/usr/bin/env python

import cgi
import os
import sys
import rtorrent
import torrentHandler
import login
import system
import config

class Index:
    def __init__(self):
        pass
    def index(self, password=None, view=None, sortby=None, reverse=None):
        if not view or view not in ["main","started","stopped","complete","incomplete","hashing","seeding","active"]:
            view = "main"
        if not sortby:
            sortby = "none"

        Config = config.Config()

        RT = rtorrent.rtorrent(Config.get("rtorrent_socket"))
        handler = torrentHandler.Handler()

        torrentList = RT.getTorrentList2(view)
        html = handler.torrentHTML(torrentList, sortby, view, reverse)

        def genHTML(type, VIEW):
            if VIEW == type:
                return  '<div class="topbar-tab selected" onmouseover="select_tab(this);" onmouseout="deselect_tab(this);" onclick="navigate_tab(this);" title="%s" id="tab_%s">%s</div>' % (type, type, type.capitalize())
            else:
                return '<div class="topbar-tab" onmouseover="select_tab(this);" onmouseout="deselect_tab(this);" onclick="navigate_tab(this);" title="%s" id="tab_%s">%s</div>' % (type, type, type.capitalize())
           

        ttmain = genHTML("main", view)
        ttstarted = genHTML("started",view)
        ttstopped = genHTML("stopped",view)
        ttcomplete = genHTML("complete",view)
        ttincomplete = genHTML("incomplete",view)
        tthashing = genHTML("hashing",view)
        ttseeding = genHTML("seeding",view)
        ttactive = genHTML("active",view)

        if not reverse:
            reverse = "none"
        else:
            reverse = "true"
            
        html_insert = """
              <div id="header">
                <div id="topbar">
                    %(main)s
                    %(started)s
                    %(stopped)s
                    %(complete)s
                    %(incomplete)s
                    %(hashing)s
                    %(seeding)s
                    %(active)s
                    <div id="tools-bar">
                        <div class="topbar-tab_options" onmouseover="select_tab(this);" onmouseout="deselect_tab(this);" onclick="navigate_options(this);" title="Options" id="tab_options">Options</div>
                    </div>
                  </div>
                  <div id="actions-bar">
                    <a href="#" id="add-torrent-button">Add torrent</a>
                  </div>
                </div>
                <div id="main_body">
                  <div id="wrapper">
                    <div id="add_torrent" style="display: none" title="Add a torrent">
                      <h3>Add torrent</h3>
                      <form id="add_torrent_form" action="ajax" method="post" enctype="multipart/form-data">
                        <input type="hidden" class="hidden" name="request" value="upload_torrent">
                        <input type="hidden" class="hidden" name="torrent_id" value="none">
                        <input id="add_torrent_input" accept="application/x-bittorrent" type="file" name="torrent">
                        <div class="add_torrent_start_text"> 
                        <input id="add_torrent_start" type="checkbox" name="start"> Start Immediately?
                        </div>
                      </form>
                    </div>
                    <div id="global_stats">
                        %(global_stats)s
                    </div>
                    <button class="hidden" onclick="refresh_content();">Click!</button>
                    <div id="this_view" class="hidden">%(view)s</div>
                    <div id="this_sort" class="hidden">%(sortby)s</div>
                    <div id="this_reverse" class="hidden">%(reverse)s</div>
        """ % {
            "main" : ttmain,
            "started" : ttstarted,
            "stopped" : ttstopped,
            "complete" : ttcomplete,
            "incomplete" : ttincomplete,
            "hashing" : tthashing,
            "seeding" : ttseeding,
            "active" : ttactive,
            "global_stats" : system.generalHTML(),
            "view" : view,
            "sortby" : sortby,
            "reverse" : reverse,
        }
        return html.replace("<!-- BODY PLACEHOLDER -->",html_insert).replace("</body>","</div></div>\n\t</body>")

