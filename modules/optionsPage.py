#!/usr/bin/env python

import config

class Options:
    def __init__(self):
        self.C = config.Config()
    
    def index(self):
        #PyRT:
            #change password
            #change port
            #(change theme)
        #rTorrent
            #global upload throttle
            #global download throttle
        HTML = """
            <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
            <html>
                <head>
                    <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
                    <title> PyRT Options </title>
                    <link rel="stylesheet" href="/css/options.css" type="text/css">
                    <script src="/javascript/jquery-1.6.1.min.js" type="text/javascript"></script>
                    <script src="/javascript/jquery-ui-1.8.13.custom.min.js" type="text/javascript"></script>
                    <script src="/javascript/options.js" type="text/javascript"></script>
                </head>
                <body>
                    <div id="header">
                        <div id="topbar">
                            <div class="topbar-tab" onmouseover="select_tab(this);" onmouseout="deselect_tab(this);" title="Main" id="tab_main">Main</div>
                            <div id="slide-me">
                                <div class="topbar-tab" onmouseover="select_tab(this);" onmouseout="deselect_tab(this);" title="Started" id="tab_started">Started</div>
                                <div class="topbar-tab" onmouseover="select_tab(this);" onmouseout="deselect_tab(this);" title="Stopped" id="tab_stopped">Stopped</div>
                                <div class="topbar-tab" onmouseover="select_tab(this);" onmouseout="deselect_tab(this);" title="Complete" id="tab_complete">Complete</div>
                                <div class="topbar-tab" onmouseover="select_tab(this);" onmouseout="deselect_tab(this);" title="Incomplete" id="tab_incomplete">Incomplete</div>
                                <div class="topbar-tab" onmouseover="select_tab(this);" onmouseout="deselect_tab(this);" title="Hashing" id="tab_hashing">Hashing</div>
                                <div class="topbar-tab" onmouseover="select_tab(this);" onmouseout="deselect_tab(this);" title="Seeding" id="tab_seeding">Seeding</div>
                                <div class="topbar-tab" onmouseover="select_tab(this);" onmouseout="deselect_tab(this);" title="Active" id="tab_active">Active</div>
                            </div>
                            <div id="tools-bar">
                                <div class="topbar-tab_options selected" onmouseover="select_tab(this);" onmouseout="deselect_tab(this);" title="Options" id="tab_options">Options</div>
                                <div class="topbar-tab_options hidden" onmouseover="select_tab(this);" onmouseout="deselect_tab(this);" title="PyRT Options" id="tab_pyrt">PyRT</div>
                                <div class="topbar-tab_options hidden" onmouseover="select_tab(this);" onmouseout="deselect_tab(this);" title="rTorrent Options" id="tab_rtorrent">rTorrent</div>
                            </div>
                        </div>
                    </div>
                    <div id="main_body">
                        <div id="wrapper">
                            <div id="pyrt-options-wrapper">
                                <h3 id="pyrt-options-h3">PyRT Options</h3>
                                <div id="pyrt-options-div">
                                    <form action="" method="POST">
                                        <div id="change_port" class="sub_option">
                                            <span class="column-1">Change Port:</span>
                                            <span class="column-2">
                                                <input type="text" id="pyrt-changeport-input" name="port" value="%(pyrt_port)s">
                                            </span>
                                        </div>
                                        <div class="row">
                                            <div id="change_password" class="sub_option">
                                                <div class="column-1 sub_heading">Change Password</div>
                                                <span class="column-1">Current Password:</span>
                                                <span class="column-2"><input type="password" id="pyrt-curpw-input" name="current_password"></span>
                                                <span class="column-1">New Password:</span>
                                                <span class="column-2"><input type="password" id="pyrt-newpw-input" name="new_password"></span>
                                                <span class="column-1">Confirm:</span>
                                                <span class="column-2"><input type="password" id="pyrt-newpw_confirm-input"> <span id="pyrt-newpw_report-span"></span></span>
                                            </div>
                                        </div>
                                    </form>
                                    
                                </div>
                            </div>
                            <div id="rtorrent-options-wrapper">
                                <h3 id="rtorrent-options-h3">rTorrent Options</h3>
                                <div id="rtorrent-options-div">
                                </div>
                            </div>
                        </div>
                    </div>
                </body>
            </html>
        """ % {
            "pyrt_port" : self.C.get("port")
        }
        
        return HTML
    
"""
    Options
    pyrt config:
        port
        host
        rtorrent_socket
        password
    rtorrent config:
        global upload throttle
        global download throttle
"""