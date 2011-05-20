$(document).ready(function () {
     setTimeout(refresh_content, 10000);
    $("#add-torrent-button").click(function(){
      $("#add_torrent").dialog("open");
    })
    $("#add_torrent").dialog({
          height: 220,
          width: 420,
          modal: true,
          autoOpen: false,
          buttons: {
                  "Add torrent": function() {
                     if (!($("#add_torrent_input").val())) {
                          $("#add_torrent_form").css("border","1px solid red");
                      } else {
                        $("#add_torrent_form").submit();
                      }
                  },
                  Cancel: function() {
                    $( this ).dialog( "close" );
                  }
                }
        });
    $(".torrent-div.rcstart").contextMenu("right_click_start", {
        bindings : {
            "start" : function (t) {
                var torrent_id = t.id.split("torrent_id_")[1];
                command("start_torrent", torrent_id);
            },
            "stop" : function (t) {
                var torrent_id = t.id.split("torrent_id_")[1];
                command("stop_torrent", torrent_id);            
            },
            "remove" : function (t) {
                var torrent_id = t.id.split("torrent_id_")[1];
                command("remove_torrent", torrent_id);
            },
            "delete" : function (t) {
                var torrent_id = t.id.split("torrent_id_")[1];
                command("delete_torrent", torrent_id);
            },
            "rehash" : function (t) {
                var torrent_id = t.id.split("torrent_id_")[1];
                command("hash_torrent", torrent_id);
            },
        },
        menuStyle : {
            minWidth : "10em"
        }
    });
    $(".torrent-div.rcpause").contextMenu("right_click_pause", {
        bindings : {
            "pause" : function (t) {
                var torrent_id = t.id.split("torrent_id_")[1];
                command("pause_torrent", torrent_id);
            },
            "stop" : function (t) {
                var torrent_id = t.id.split("torrent_id_")[1];
                command("stop_torrent", torrent_id);            
            },
            "remove" : function (t) {
                var torrent_id = t.id.split("torrent_id_")[1];
                command("remove_torrent", torrent_id);
            },
            "delete" : function (t) {
                var torrent_id = t.id.split("torrent_id_")[1];
                command("delete_torrent", torrent_id);
            },
            "rehash" : function (t) {
                var torrent_id = t.id.split("torrent_id_")[1];
                command("hash_torrent", torrent_id);
            },
        },
        menuStyle : {
            minWidth : "10em"
        }
    });
    $("#tab_options").bind(
                           "click",
                           function () {
                            window.location = "/options";
                           }
                           );
});

function refresh_content() {
    // get all torrent ids on page
    req = "/ajax?request=get_info_multi&view=" + $("#this_view").html()
    if (!($("#this_sort").html() === "none")) {
        req += "&sortby=" + $("#this_sort").html();
    }
    if (!($("#this_reverse").html() === "none")) {
        req += "&reverse=" + $("#this_reverse").html();
    }
    $.getJSON(req, function (data) {
        $("#global_stats").html(data.system);
        
        // data has structure:
            //{
            //    "torrents" : {},
            //    "system" : system_html,
            //    "torrent_index" : [id, id, id] // this is in the order that they are arranged in the page (or should be if this has changed)
            //}
        torrent_list = $("#torrent_list").find($("tr")).filter(
            function (index) {
                return (!($(this).attr("id").indexOf("torrent_id_") === -1))
            }
        )
        cur_t_ids = new Array();
        for (i=0; i<torrent_list.length; i++) {
            torrent_id = $(torrent_list[i]).attr("id").split("torrent_id_")[1];
            cur_t_ids.push(torrent_id);
            if (data.torrent_index.indexOf(torrent_id) == -1) {
                // remove_torrentrow(id)
            } else {
                // refresh torrent data
                torrent_data = data.torrents[torrent_id];
                // returned data: ratio, uprate, downrate, status
                $("#t_ratio_" + torrent_id).html(torrent_data.ratio);
                $("#t_uprate_" + torrent_id).html(torrent_data.uprate + "/s");
                $("#t_downrate_" + torrent_id).html(torrent_data.downrate + "/s");
                $("#t_status_" + torrent_id).html(torrent_data.status);
            }
        }
          
        // check for new torrents and add them
        for (i=0; i<data.torrent_index.length; i++) {
            torrent_id = data.torrent_index[i];
            if ($.inArray(torrent_id, cur_t_ids) === -1) {
                add_torrentrow(torrent_id, data.torrents[torrent_id])
            }
        }
        
        setTimeout(refresh_content, 10000);
    });
}

function add_torrentrow(torrent_id, torrent_data) {
    req = "/ajax?request=get_torrent_info&torrent_id=" + torrent_id;
    $.getJSON(req, function (response) {
        var torrent_rows = $("#torrent_table").children(".torrent-div");
        // get colour of first element
        if ($(torrent_rows.get(0)).hasClass("blue")) {
            var newcolour = "green";
        } else {
            var newcolour = "blue";
        }
        alert("newcolour: " + newcolour);
        
        // construct element using native js methods
        var newtorrentrow = document.createElement("tr");
        newtorrentrow.id = "torrent_id_" + torrent_id;
        alert("newtorrentrow: " + $(newtorrentrow).html())
        var attribs = new Array(
            Array("name", response.name),
            Array("size", response.size),
            Array("ratio", response.ratio),
            Array("uprate", torrent_data.uprate + "/s"),
            Array("downrate", torrent_data.downrate + "/s"),
            Array("status", torrent_data.status)
            // Array("controls", )
        );
        for (i=0; i<attribs.length; i++) {
            keyval = attribs[i];
            alert("keyval: " + keyval);
        }
        
    // var torrent_id = elem.id.split("torrent_id_")[1];
    // var table = document.getElementById("torrent_list");
    // if (oldrow = document.getElementById('newrow_torrent_id_' + torrent_id)) {
        // table.deleteRow(oldrow.rowIndex);
    // }
    // var newrow = table.insertRow(elem.rowIndex + 1);
    // var newcell = newrow.insertCell(0);
    // newrow.id = "newrow_torrent_id_" + torrent_id;
    // newrow.className += " drop_down";
    // newcell.innerHTML = "<img src='/images/loading.gif'> <span style='color:red;'>Loading</span>";
    // newcell.colSpan = "7";
                // <tr onmouseover='select_torrent(this);' 
                    // onmouseout='deselect_torrent(this);' 
                    // onclick='view_torrent(this);'
                    // ondblclick='navigate_torrent(this);'
                    // class='torrent-div blue rcstart' 
                    // id='torrent_id_9C3E55AAA05E5B9F5369FADF084EC77EF108903C'> 
                    // <td id="t_name_9C3E55AAA05E5B9F5369FADF084EC77EF108903C">FILMS</td> 
                    // <td id="t_size_9C3E55AAA05E5B9F5369FADF084EC77EF108903C">3.43 GB</td> 
                    // <td id="t_ratio_9C3E55AAA05E5B9F5369FADF084EC77EF108903C" title='0 B up / 0 B down'>0.00</td> 
                    // <td id="t_uprate_9C3E55AAA05E5B9F5369FADF084EC77EF108903C">0 B/s</td> 
                    // <td id="t_downrate_9C3E55AAA05E5B9F5369FADF084EC77EF108903C">0 B/s</td> 
                    // <td id="t_status_9C3E55AAA05E5B9F5369FADF084EC77EF108903C">Stopped</td> 
                    // <td id="t_controls_9C3E55AAA05E5B9F5369FADF084EC77EF108903C"> 
                        // <span class='control_start control_button' title='Start Torrent'><img onclick='event.cancelBubble = true; command("start_torrent","9C3E55AAA05E5B9F5369FADF084EC77EF108903C")' class='control_image' alt='Start' src='../images/start.png'></span> 
                        // <span class='control_stop control_button' title='Stop Torrent'> 
                            // <img onclick='event.cancelBubble = true; command("stop_torrent","9C3E55AAA05E5B9F5369FADF084EC77EF108903C")'
                                 // class='control_image' alt='Stop' src='../images/stop.png'> 
                        // </span> 
                        // <span class='control_remove control_button' title='Remove Torrent'> 
                            // <img onclick='event.cancelBubble = true; command("remove_torrent","9C3E55AAA05E5B9F5369FADF084EC77EF108903C")'
                                 // class='control_image' alt='Remove' src='../images/remove.png'> 
                        // </span> 
                        // <span class='control_delete control_button' title='Remove Torrent and Files'> 
                            // <img onclick='event.cancelBubble = true; command("delete_torrent","9C3E55AAA05E5B9F5369FADF084EC77EF108903C")'
                                 // class='control_image' alt='Delete' src='../images/delete.png'> 
                        // </span> 
                    // </td> 
                // </tr> 

    });
}

function select_torrent(elem) {
    // elem.style.backgroundColor = "#00CCFF";
    elem.style.backgroundColor = "#0099FF";
    elem.style.cursor = "help";
}
function deselect_torrent(elem) {
    elem.style.backgroundColor = null;
    elem.style.cursor = "default";
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

function navigate_torrent(elem) {
    window.location = "detail?torrent_id=" + elem.id.split("torrent_id_")[1]
}

function removerow(torrent_id) {
    if (row = document.getElementById("newrow_torrent_id_" + torrent_id)) {
        var table = document.getElementById("torrent_list");
        table.deleteRow(row.rowIndex);
    }
    
}
function view_torrent(elem) {
    var torrent_id = elem.id.split("torrent_id_")[1];
    var table = document.getElementById("torrent_list");
    if (oldrow = document.getElementById('newrow_torrent_id_' + torrent_id)) {
        table.deleteRow(oldrow.rowIndex);
    }
    var newrow = table.insertRow(elem.rowIndex + 1);
    var newcell = newrow.insertCell(0);
    newrow.id = "newrow_torrent_id_" + torrent_id;
    newrow.className += " drop_down";
    newcell.innerHTML = "<img src='/images/loading.gif'> <span style='color:red;'>Loading</span>";
    newcell.colSpan = "7";
    var xmlhttp = new XMLHttpRequest();
    var url="ajax"
    xmlhttp.open("POST",url,true);
    xmlhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            var response = xmlhttp.responseText;
            newcell.innerHTML = response;
        }
    }
    var params = "request=get_torrent_info&html=yesplease&torrent_id=" + torrent_id;
    xmlhttp.send(params);
}

function command(cmd, t_id) {
    if (cmd === "pause_torrent" || cmd === "start_torrent" || cmd === "stop_torrent" || cmd == "remove_torrent" || cmd == "delete_torrent" || cmd == "hash_torrent") {
        var resp;
        if (cmd === "remove_torrent") {
            resp = confirm("Are you sure you want to remove this torrent?");
        } else if (cmd == "delete_torrent") {
            resp = confirm("Are you sure you want to remove this torrent and *permanently* delete its files?");
        } else if (cmd == "hash_torrent") {
            resp = confirm("Are you sure you want to rehash this torrent?\n This process can take a long time for large torrents");
        } else {
            resp = true;
        }
        if (resp) {
            var xmlhttpc = new XMLHttpRequest();
            var url="ajax";
            xmlhttpc.open("POST",url,true);
            xmlhttpc.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            xmlhttpc.onreadystatechange = function() {
                if (xmlhttpc.readyState == 4 && xmlhttpc.status == 200) {
                    var resp = xmlhttpc.responseText.trim()
                    if (resp === "OK") {
                        location.reload(true);
                    } else {
                        alert("Command Failed with reason: " + resp);
                    }
                }
            }
            var params = "request=" + cmd + "&torrent_id=" + t_id;
            xmlhttpc.send(params);
        } else {
            return false;
        }
    } else {
        alert("invalid command or command not implemented");
    }
}