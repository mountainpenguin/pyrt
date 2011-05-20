$(document).ready(function () {
     setTimeout(function () {
        refresh_content("yes");
     }, 5000);
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
    loadRClickMenus();
});

function loadRClickMenus() {
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
}
function refresh_content(repeat) {
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
                remove_torrentrow(torrent_id)
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
        
        if (repeat === "yes") {
            setTimeout(function () {
                refresh_content("yes");
            }, 5000);
        }
    });
}

function remove_torrentrow(torrent_id) {
    if (row = document.getElementById("torrent_id_" + torrent_id)) {
        row.style.border = "none";
        row.style.backgroundColor = "red";
        $(row).fadeOut(2000, function () {
            document.getElementById("torrent_list").deleteRow(row.rowIndex);
        });
    }
}

function add_torrentrow(torrent_id, torrent_data) {
    req = "/ajax?request=get_torrent_info&torrent_id=" + torrent_id;
    $.getJSON(req, function (response) {
        var torrent_table = document.getElementById("torrent_list");
        firstTRow = torrent_table.getElementsByTagName("tbody")[0].getElementsByTagName("tr")[1];
        if (firstTRow.className.indexOf("blue") === -1) {
            var newcolour = "blue";
        } else {
            var newcolour = "green";
        }
        
        // construct element using native js methods
        var newtorrentrow = torrent_table.insertRow(1);
        newtorrentrow.id = "torrent_id_" + torrent_id;
        newtorrentrow.style.display = "none";
        newtorrentrow.style.backgroundColor = "#CDE472";
        
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
            newcell = newtorrentrow.insertCell(-1);
            newcell.id = "t_" + keyval[0] + "_" + torrent_id;
            newcell.innerHTML = keyval[1];
        }
        
        controlcell = newtorrentrow.insertCell(-1);
        controlcell.id = "t_controls_" + torrent_id;
        
        if (torrent_data.status === "Stopped" || torrent_data.status === "Paused") {
            controlcell.appendChild(create_controlSpan("Start", "start", torrent_id));
        } else {
            controlcell.appendChild(create_controlSpan("Pause", "pause", torrent_id));
        }
        controlcell.appendChild(create_controlSpan("Stop", "stop", torrent_id));
        controlcell.appendChild(create_controlSpan("Remove", "remove", torrent_id));
        controlcell.appendChild(create_controlSpan("Delete", "delete", torrent_id));
        
        if (torrent_data.status === "Stopped" || torrent_data.status === "Paused") {
            newtorrentrow.className = "torrent-div " + newcolour + " rcstart";
        } else {
            newtorrentrow.className = "torrent-div " + newcolour + " rcstop";
        }
        $("#torrent_id_" + torrent_id).bind(
            "click",
            function (event) {
                view_torrent(this);
            }
        );
        $("#torrent_id_" + torrent_id).bind(
            "mouseover",
            function (event) {
                select_torrent(this);
            }
        );
        $("#torrent_id_" + torrent_id).bind(
            "mouseout",
            function (event) {
                deselect_torrent(this);
            }
        );
        $("#torrent_id_" + torrent_id).bind(
            "dblclick",
            function (event) {
                navigate_torrent(this)
            }
        );
        
        $(newtorrentrow).fadeIn(2000, function() {
            newtorrentrow.style.backgroundColor = null;
            loadRClickMenus() 
        });
    });
}

function create_controlSpan(alt, name, torrent_id) {
    span = document.createElement("span");
    span.className = "control_" + name + " control_button";
    span.title = alt + " Torrent";
    image = document.createElement("img");
    image.className = "control_image";
    image.alt = alt;
    image.src = "/images/" + name + ".png";
    image.style.cursor = "pointer";
    image.style.paddingRight = "3px";
    $(image).bind(
        "click",
        function (event) {
            event.cancelBubble;
            command(name + "_torrent","" + torrent_id);
            return false;
        }
    );
    span.appendChild(image);
    return span;
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
                    if (resp == "OK") {
                        refresh_content("no");
                    else {
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