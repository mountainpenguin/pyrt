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

var ls = null;
if (window.document.location.protocol == "https:") {
     var socket_protocol = "wss"
} else {
     var socket_protocol = "ws"
}

var hiddenclasstypes = new Array();

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

$(document).ready(function () {
    ls = new window.WebSocket(socket_protocol + "://" + window.document.location.host + "/logsocket");
    ls.onmessage = onMessage;
    ls.onerror = function (evt) {
        console.log("logSocket error", evt, ls);
    }
    ls.onopen = function (evt) {
        console.log("logSocket opened", evt, ls);
    }
    ls.onclose = function (evt) {
        console.log("logSocket closed", evt, ls);
    }

    // bind to changes in "selection" buttons
    $(".log_control").bind("click", function(e) {
        if ($(this).hasClass("selected")) {
            if ( $(this).attr("id") == "log_control_1" ) {
                $(".log_message.level_1").addClass("hidden_message");
                hiddenclasstypes.push("level_1");
            } else if ($(this).attr("id") == "log_control_2") {
                $(".log_message.level_2").addClass("hidden_message");;
                hiddenclasstypes.push("level_2");
            } else if ($(this).attr("id") == "log_control_3") {
                $(".log_message.level_3").addClass("hidden_message");
                hiddenclasstypes.push("level_3");
            } else if ($(this).attr("id") == "log_control_4") {
                $(".log_message.level_4").addClass("hidden_message");
                hiddenclasstypes.push("level_4");
            }
            $(this).removeClass("selected");
        } else {
            if ( $(this).attr("id") == "log_control_1" ) {
                $(".log_message.level_1").removeClass("hidden_message");
                hiddenclasstypes.splice(hiddenclasstypes.indexOf("level_1"), 1);
            } else if ($(this).attr("id") == "log_control_2") {
                $(".log_message.level_2").removeClass("hidden_message");
                hiddenclasstypes.splice(hiddenclasstypes.indexOf("level_2"), 1);
            } else if ($(this).attr("id") == "log_control_3") {
                $(".log_message.level_3").removeClass("hidden_message");
                hiddenclasstypes.splice(hiddenclasstypes.indexOf("level_3"), 1);
            } else if ($(this).attr("id") == "log_control_4") {
                $(".log_message.level_4").removeClass("hidden_message");
                hiddenclasstypes.splice(hiddenclasstypes.indexOf("level_4"), 1);
            }
            $(this).addClass("selected");
        }
    })
});

function getLatestID() {
    var table = $(".log_row:first-child");
    if (table.length) {
        return "&lastID=" + table.attr("id");
    } else {
        return "";
    }

}

function onMessage(evt) {
    var newrows = $(evt.data);
    for (i=0; i<hiddenclasstypes.length; i++) {
        if (newrows.hasClass(hiddenclasstypes[i])) {
            newrows.addClass("hidden_message");
        }
    }
    var table = $("#log_table");
    table.prepend(newrows);
    setTimeout(removeNew, 2000);
}

function removeNew() {
    $(".new_message").each( function () {
        $(this).removeClass("new_message");
    });
}
