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
		for (i=0; i<torrent_list.length; i++) {
			torrent_id = $(torrent_list[i]).attr("id").split("torrent_id_")[1];
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

function htmlify(json, cell) {
    var obj = JSON.parse(json);
    var new_html = new String();
    new_html += "<div class='drop_down'>"
    new_html += "<div class='column-1'>ID:</div><div class='column-2'>" + obj.torrent_id + "</div>"
    new_html += "<div class='column-1'>Size:</div><div class='column-2'>" + obj.size + "</div>"
    new_html += "<div class='column-1'>Percentage:</div><div class='column-2'>" + obj.percentage + "%</div>"
    new_html += "<div class='column-1'>Downloaded:</div><div class='column-2'>" + obj.downloaded  + "</div>"
    new_html += "<div class='column-1'>Uploaded:</div><div class='column-2'>" + obj.uploaded + "</div>"
    new_html += "<div class='column-1'>Ratio:</div><div class='column-2'>" + obj.ratio + "</div>"
    new_html += "<div class='column-1'>Peers:</div><div class='column-2'>" + obj.peers.length + "</div>"
    new_html += "<div class='column-1'>Created:</div><div class='column-2'>" + obj.created + "</div>"
    new_html += "<div class='column-2' style='clear : left;'><span class='fakelink' onClick='removerow(\"" + obj.torrent_id + "\")'>Close</span> <a style='color : blue;' href='detail?torrent_id=" + obj.torrent_id + "'>Detailed View</a></div>"
    new_html += "</div>"
    cell.innerHTML = new_html;
    cell.style.borderLeft="1px dotted";
    cell.style.borderRight="1px dotted";
    cell.style.backgroundColor = "#eeeeee";
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
    newcell.innerHTML = "<img src='/images/loading.gif'> <span style='color:red;'>Loading</span>";
    newcell.colSpan = "7";
    var xmlhttp = new XMLHttpRequest();
    var url="ajax"
    xmlhttp.open("POST",url,true);
    xmlhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            var response = xmlhttp.responseText;
            // newcell.innerHTML = response;
            htmlify(response, newcell);
        }
    }
    var params = "request=get_torrent_info&torrent_id=" + torrent_id;
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