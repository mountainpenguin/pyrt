var ls = null;
if (window.document.location.protocol == "https:") {
     var socket_protocol = "wss"
} else {
     var socket_protocol = "ws"
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

$(document).ready(function () {
    ls = new window.WebSocket(socket_protocol + "://" + window.document.location.host + "/logsocket");
    ls.onmessage = onMessage;
    ls.onerror = function (evt) {
        console.log("logSocket error", evt, ls);
    }
    ls.onopen = function (evt) {
        console.log("logSocket opened", evt, ls);
        mainLoop();
    }
    ls.onclose = function (evt) {
        console.log("logSocket closed", evt, ls);
    }
});

function getLatestID() {
    var table = $(".log_row:first-child");
    if (table.length) {
        return "&lastID=" + table.attr("id");
    } else {
        return "";
    }

}
function mainLoop() {
    ls.send("request=checknew" + getLatestID());
    setTimeout(mainLoop, 10000); 
}

function onMessage(evt) {
    var newrows = $(evt.data);
    var table = $("#log_table");
    table.prepend(newrows);
    setTimeout(removeNew, 2000);
}

function removeNew() {
    $(".new_message").each( function () {
        $(this).removeClass("new_message");
    });
}
