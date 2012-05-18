var socket = null;
if (window.document.location.protocol == "https:") {
     var socket_protocol = "wss"
} else {
     var socket_protocol = "ws"
}

$(document).ready( function () {
    socket = new window.WebSocket(socket_protocol + "://" + window.document.location.host + "/ircsocket");
    socket.onmessage = OnMessage;
    socket.onerror = function (evt) {
        console.log("ircSocket error", evt, socket);
    }
    socket.onopen = function (evt) {
        console.log("ircSocket opened", evt, socket);
    }
    socket.onclose = function (evt) {
        console.log("ircSocket closed", evt, socket);
    }
   
    $("#clicktest").bind("click", function () {
        socket.send("test");
    });
});

function OnMessage (evt) {
    console.log("ircSocket message", evt.data);
}
