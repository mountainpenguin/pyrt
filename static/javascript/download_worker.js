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

if (location.protocol == "http:") {
    var socket_protocol = "ws:";
} else {
    var socket_protocol = "wss:";
}
var sock = new WebSocket(socket_protocol + "//" + location.host + "/workersocket");
var SOCKOPEN = false;

sock.onmessage = function (event) {
    parentSend("Worker got socket response: " + event.data);
    var r = JSON.parse(event.data);
    if (r.error) {
        parentSend("Worker encountered an error! " + r.error);
        return false;
    }
    var request = r.request;
    var response = r.response;
    if (request == "prepare") {
        onPrepare(response);
    }
}
sock.onopen = function (event) {
    SOCKOPEN = true;
}
sock.onclose = function (event) {
    SOCKOPEN = false;
}
sock.onerror = function (event) {
    
}

self.onmessage = function (event) {
    var msg = JSON.parse(event.data);
    parentSend("Worker received command: " + msg.command);
    if (msg.command == "start_download") {
        var t_id = msg.content.torrent_id;
        parentSend("Worker got torrent_id: " + t_id);
        initialise(t_id);
    }
}

function initialise(t_id) {
    sockSend("prepare", [t_id]);
}

function onPrepare(response) {
    parentSend("Worker has file list, first file path: " + response[0].abs_path);
}

function parentSend(message) {
    self.postMessage(message);
}

function sockSend(request, content) {
    if (SOCKOPEN) {
        msgObj = {
            "request" : request,
            "content" : content,
        }
        sock.send(JSON.stringify(msgObj));
    } else {
        setTimeout(sockSend, 1000, request, content);
    }
}