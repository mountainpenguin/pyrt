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

var args = null;
var socket = null;

if (window.document.location.protocol == "https:") {
     var socket_protocol = "wss"
} else {
     var socket_protocol = "ws"
}

$(document).ready( function () {
    var pn = window.location.pathname;
    socket = new window.WebSocket(
        socket_protocol + "://" + window.location.host + pn.substring(0, pn.lastIndexOf("/") + 1) + "autosocket"
    );

    socket.onmessage = onMessage; // defined in auto-irc.js or auto-rss.js
    socket.onerror = function (evt) {
        console.log("autoSocket error", evt, socket);
    }
    socket.onopen = onOpen; // defined in auto-irc.js or auto-rss.js
    socket.onclose = function (evt) {
        console.log("autoSocket closed", evt, socket);
    }

    var socketrefresh = setInterval(
        function(){
            socket.send("ping")
        }, 1000 * 40
    );

    $(".filter_select").live("change", function() {
        var selectelem = $("<select class='filter_select'><option selected='selected'>---</option><option>and</option><option>not</option><option>size</option></select>");
        var andinput = $("<input name='add_filter' class='input_filter positive' type='text' placeholder='Positive Filter' />");
        var notinput = $("<input name='not_filter' class='input_filter negative' type='text' placeholder='Negative Filter' />");
        var sizeinput = $("<input class='input_filter size lower' type='number' placeholder='Lower' min=0 /> \
                                <select class='size_select'> \
                                    <option value=1073741824>GB</option> \
                                    <option value=1048576>MB</option> \
                                    <option value=1024>KB</option> \
                                    <option value=1>B</option> \
                                </select> \
                            <input class='input_filter size upper' type='number' placeholder='Upper' min=0 /> \
                                <select class='size_select'> \
                                    <option value=1073741824>GB</option> \
                                    <option value=1048576>MB</option> \
                                    <option value=1024>KB</option> \
                                    <option value=1>B</option> \
                                </select>");
        if ($(this).val() == "---") {
            if ($(this).parent().children("select").length == 2 || $(this).parent().children("select").length == 4) {
                $(this).parent().prev().append($(this));
                $(this).parent().next().remove();
            } else {
                $(this).parent().remove();
            }
        } else if ($(this).val() == "and") {
            if ($(this).next().length > 0) {
                if ( $(this).parent().hasClass("size_filter") ) {
                    $(this).next().replaceWith(andinput);
                    for (i=0; i<3; i++) {
                        $(this).next().next().remove();
                    }
                }
                $(this).parent().removeClass("not_filter size_filter");
                $(this).parent().addClass("and_filter");
                $(this).next().attr("placeholder", "Positive Filter");
                return;
            }
            $(this).parent().after(
                $("<div class='and_filter' />")
                .append(andinput)
                .append(selectelem)
            );
            $(this).parent().next().prepend($(this));
        } else if ($(this).val() == "not") {
            if ($(this).next().length > 0) {
                if ( $(this).parent().hasClass("size_filter") ) {
                    $(this).next().replaceWith(notinput);
                    for (i=0; i<3; i++) {
                        $(this).next().next().remove();
                    }
                }
                $(this).parent().removeClass("and_filter size_filter");
                $(this).parent().addClass("not_filter");
                $(this).next().attr("placeholder", "Negative Filter");
                return;
            }
            $(this).parent().after(
                $("<div class='not_filter' />")
                .append(notinput)
                .append(selectelem)
            );
            $(this).parent().next().prepend($(this));
        } else if ($(this).val() == "size") {
            if ($(this).next().length > 0) {
                $(this).parent().removeClass("and_filter not_filter");
                $(this).parent().addClass("size_filter");
                $(this).next().remove();
                $(this).after(sizeinput);
                return;
            }
            $(this).parent().after(
                $("<div class='size_filter' />")
                .append(sizeinput)
                .append(selectelem)
            );
            $(this).parent().next().prepend($(this));
        }
    });
});
