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

$(document).ready( function() {
    $("#add_feed").click( function () {
        var state = $("#add_feed_txt");
        if (state.hasClass("selected")) {
            //$("#add_feed_hidden").addClass("hidden");
            $("#add_feed_hidden").slideUp("fast");
            state.removeClass("selected");
        } else {
            //$("#add_feed_hidden").removeClass("hidden");
            $("#add_feed_hidden").slideDown("fast");
            state.addClass("selected");
        }
    });
    $("input.error").live("keydown", function () {
        $(this).removeClass("error");
    });
    $("#rss_submit").click( function () {
        var inputs = new Array();
        var alias = $("#alias").val();
        var err = null;
        if (!alias) {
            $("#alias").addClass("error");
            err = true;
        }
        var ttl = $("#ttl").val();
        if (!ttl) {
            $("#ttl").addClass("error");
            err = true;
        }
        var url = $("#url").val();
        if (!url) {
            $("#url").addClass("error");
            err = true;
        }
        if (err) {
            return false;
        } else {
            socket.send("request=add_rss&alias=" + alias + "&ttl=" + ttl + "&uri=" + url)
        }
    });
});

function onOpen (evt) {
    console.log("autoSocket opened", evt, socket);
    runInit();
}

function onMessage (evt) {
    if (evt.data.indexOf("ERROR") === 0) {
        console.log(evt.data);
        socket.close();
    } else {
        var response = JSON.parse(evt.data);
        if (response.request == "get_rss") {
            if (response.error) {
                console.log("ERROR in request " + response.request + ": " + response.error);
                return false;
            }
            runPostInit(response.response);
        } else if (response.request == "add_rss") {
            if (response.error) {
                alert("ERROR in request " + response.request + ": " + response.error);
                return false;
            }
            window.location.replace(window.location);
        } else {
            console.log("socket message:", evt.data)
        }
    }
}

function runInit() {
    socket.send("request=get_rss");
}

function runPostInit(rows) {
    $("div#temp").remove();
    var table = $("table#feeds > tbody");
    for (i=0; i<rows.length; i++) {
        table.append($(rows[i]));
    }
}