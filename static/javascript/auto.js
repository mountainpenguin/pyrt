/*  Copyright (C) 2012 by mountainpenguin (pinguino.de.montana@googlemail.com)
 *  http://github.com/mountainpenguin/pyrt
 *
 *  This file is part of pyRT.
 *  
 *  pyRT is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  pyRT is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with pyRT.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

var socket = null;
if (window.document.location.protocol == "https:") {
     var socket_protocol = "wss"
} else {
     var socket_protocol = "ws"
}

$(document).ready( function () {
    socket = new window.WebSocket(socket_protocol + "://" + window.document.location.host + "/autosocket");
    socket.onmessage = OnMessage;
    socket.onerror = function (evt) {
        console.log("autoSocket error", evt, socket);
    }
    socket.onopen = function (evt) {
        console.log("autoSocket opened", evt, socket);
    }
    socket.onclose = function (evt) {
        console.log("autoSocket closed", evt, socket);
    }
   
    $("#clicktest").bind("click", function () {
        socket.send("test");
    });

    $(".topbar-tab_suboption").bind("click", function () {
        $(".sub_wrapper:not(.is_hidden)").addClass("is_hidden");
        if (this.id == "subtab_IRC") {
            $(this).addClass("selected");
            runIRCInit();
        } else if (this.id == "subtab_RSS") {
            $(this).addClass("selected");
            runRSSInit();
        } else if (this.id == "subtab_web") {
            $(this).addClass("selected");
            runWEBInit();
        }
    });
});

function runIRCInit() {
    $("#irc_wrapper").removeClass("is_hidden");
}
function runRSSInit() {
    $("#rss_wrapper").removeClass("is_hidden");
}
function runWEBInit() {
    $("#web_wrapper").removeClass("is_hidden");
}
function OnMessage (evt) {
    console.log("ircSocket message", evt.data);
}

function select_tab(elem) {
    elem.style.backgroundColor = "#bbbbbb";
}

function deselect_tab(elem) {
    elem.style.backgroundColor = null;
}

function navigate_tab(elem) {
    window.location = "?view=" + elem.id.split("tab_")[1];
}

function navigate_tab_toHome(elem) {
    window.location = "/?view=" + elem.id.split("tab_")[1];
}
