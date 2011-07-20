#!/usr/bin/env python

import cgi
import os
import sys
import config

class Index:
    def __init__(self):
        self.TEMPLATE_MAIN = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
    <head>
        <!-- HEAD PLACEHOLDER -->
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
        <title>rTorrent - RSS</title>
        
        <link rel="stylesheet" type="text/css" href="/css/main.css">
        <link rel="stylesheet" type="text/css" href="/css/smoothness/jquery-ui-1.8.13.custom.css">                
        <script src="/javascript/jquery-1.6.1.min.js" type="text/javascript"></script>
        <script src="/javascript/jquery-ui-1.8.13.custom.min.js" type="text/javascript"></script>        
        <script src="/javascript/jquery.contextmenu.r2.js" type="text/javascript"></script>
        <script src="/javascript/jquery-sliderow.js" type="text/javascript"></script>
        <script src="/javascript/rss.js" type="text/javascript"></script>
        
    </head>
    <body>
        <div id="header">
            <div id="topbar">
                <div class="topbar-tab" onmouseover="select_tab(this);" onmouseout="deselect_tab(this);" onclick="navigate_tab_fromRSS(this);" title="main" id="tab_main">Main</div>
                <div class="topbar-tab_options selected" onmouseover="select_tab(this);" onmouseout="deselect_tab(this);" onclick="navigate_tab(this);" title="RSS" id="tab_RSS">RSS</div>
            </div>
        </div>
        <div id="main_body">
            <div id="wrapper">
                <div id="feed_wrapper">
                    <span><img src="static/images/loading.gif" title="Loading..." alt="Loading..."></span>
                </div>
                <div class="feed_add"><button>Add Feed</button></div>
            </div>
        </div>
    </body>
</html>
        """
    
    def index(self, password=None):
        return self.TEMPLATE_MAIN       
