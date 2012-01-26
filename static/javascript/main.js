var CTRL_SELECTED = false;
var SELECTED = new Array();

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
     stripeTable();
     $(document).keydown(function (e) {
          if (((e.ctrlKey) || (e.which == 91))  && !(CTRL_SELECTED))  {
               CTRL_SELECTED = true;
               $("#torrent_table").selectable({
                    filter : ".torrent-div",
                    tolerance : "touch"
               })
               $("body").css({cursor : "copy"});
               e.preventDefault();
               e.stopPropagation();
          }
     });
     $(document).keyup(function (e) {
          if ((e.which == 17) || (e.which == 91) && CTRL_SELECTED) {
               CTRL_SELECTED = false;
               $("#torrent_table").selectable("destroy");
               $("body").css("cursor", "");
          }
     })
     
     $(".torrent-div").click(function (e) {
          if (e.ctrlKey) {
          } else {
               view_torrent(this);
          }
     })
     $(".batch-control").live("click", function (e) {
          action = this.id.split("batch-")[1];
          torrentIDs = new Array();
          for (i=0; i<SELECTED.length; i++) {
               torrentIDs.push(SELECTED[i].split("torrent_id_")[1]);
          }
          if (action == "delete" || action == "remove") {
               SELECTED = new Array();
               destroyBatchActionBox();
          }
          $.post(
               "/ajax",
               {
                    "request" : action + "_batch",
                    "torrentIDs" : torrentIDs.join(",")
               }
          );
     })
     $("#batch-deselect").live("click", function (e) {
          for (i=0; i<SELECTED.length; i++) {
               torrent = $("#" + SELECTED[i]);
               torrent.css({"background-color" : ""});
               torrent.removeClass("ui-selected ui-selecting");
          }
          SELECTED = new Array();
          destroyBatchActionBox();
     })

     $("#torrent_table")
       .live("selectableselected", function(event, ui) {
          select_group_torrent(ui.selected, event);
     }).live("selectableunselected", function(event, ui) {
          deselect_group_torrent(ui.unselected, event);
     }).live("selectableselecting", function(event, ui) {
          if (SELECTED.indexOf(ui.selecting.id) == -1) {
               $(ui.selecting).css({"background-color" : "#d9ffd9"});
          }
     }).live("selectableunselecting", function(event, ui) {
          if (SELECTED.indexOf(ui.unselecting.id) == -1) {
               $(ui.unselecting).css({"background-color" : ""});
          }
     })
});
function select_group_torrent(elem, e) {
     sel_index = SELECTED.indexOf(elem.id);
     if (sel_index !== -1) {
     } else {
          SELECTED.push(elem.id);
          elem.style.backgroundColor = "#AEC798";
          if (SELECTED.length == 1) {
               createBatchActionBox(e.pageX, e.pageY);
          }
     }
}
function deselect_group_torrent(elem, e) {
     sel_index = SELECTED.indexOf(elem.id);
     if (sel_index != -1) {
          SELECTED.splice(sel_index, 1);
          $(elem).css({"background-color" : ""});
          if (SELECTED.length == 0) {
               destroyBatchActionBox();
          }
     }
}
function createBatchActionBox(x, y) {
     batchActionsBox = $("<div id='batchActionBox'></div>");
     head = $("<div id='batch-head' class='heading'>Batch Action</div>");
     
     start = $("<img class='batch-control' id='batch-start' src='../images/start.png' title='Start Batch'>");
     pause = $("<img class='batch-control' id='batch-pause' src='../images/pause.png' title='Pause Batch'>");
     stop = $("<img class='batch-control' id='batch-stop' src='../images/stop.png' title='Stop Batch'>");
     startpausestop = $("<div id='batch-control-row1'></div>").append(start, pause, stop);
     
     remove = $("<img class='batch-control' id='batch-remove' src='../images/remove.png' title='Remove Batch'>");
     del = $("<img class='batch-control' id='batch-delete' src='../images/delete.png' title='Delete Batch'>");
     startpausestop.append(remove, del);
     
     deselect = $("<div id='batch-deselect'>Deselect all</div>");
     
     controls = $("<div id='batch-controls'></div>").append(startpausestop, deselect);
     newElem = batchActionsBox.append(head, controls);
     $("body").append(newElem);
     $("#batchActionBox").animate({"left" : "0px"}, 200);
}
function destroyBatchActionBox() {
     $("#batchActionBox").remove();
}
function stripeTable() {
    var colour_classes = Array("blue", "green");
    $(".torrent-div").each(
        function () {
            col = colour_classes.shift();
            $(this).removeClass("blue green");
            $(this).addClass(col);
            colour_classes.push(col);
        }
    );
}
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
         window.location = "/options?test=test";
         }
     );
     $("#tab_rss").bind(
         "click",
         function () {
           window.location = "/RSS";
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
            var torrent_id = $(torrent_list[i]).attr("id").split("torrent_id_")[1];
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
                var oldstatus = $("#t_status_" + torrent_id)
                if (oldstatus.html() != torrent_data.status) {
                    oldstatus.html(torrent_data.status);
                    var reqrefresh = "/ajax?request=get_torrent_row&torrent_id=" + torrent_id;
                    $.ajax({
                        url : reqrefresh,
                        context : $("#t_controls_" + torrent_id),
                        dataType : "html",
                        success : function (newrowhtml) {
                            $(this).html(
                                $("#" + $(this).attr("id"), newrowhtml).html()
                            );
                        },
                        error : function (jqXHR, textStatus, errorThrown) {
                            alert("Error " + jqXHR + " (" + errorThrown + ")");
                        }
                    });
                }
                
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
    var row = $("#torrent_id_" + torrent_id);
    if (row.length != 0) {
        $(row).removeClass("blue green").toggleClass("old-torrent-row");
        $(row).effect("pulsate", { times : 1 }, "slow", function() {
            $(row).fadeTo(2000, 0.1, function() {
                $(this).slideRow("up", 1000, function() {
                    $("#torrent_id_" + torrent_id).remove();
                    stripeTable();
                });
            });
        });
    }
}

function add_torrentrow(torrent_id, torrent_data) {
    var req = "/ajax?request=get_torrent_row&torrent_id=" + torrent_id;
    var torrent_list = $("#torrent_list");
    $.ajax({
        url : req,
        context : torrent_list,
        dataType : "html",
        success : function (newrowhtml) {
            $("#torrent_list > tbody > tr:eq(0)").after($(newrowhtml));
            var newrow = $("#torrent_id_" + torrent_id);
            $(newrow).toggleClass("new-torrent-row");
            $(newrow).slideRow("down", 1000, function () {
                $(newrow).fadeTo(2000, 1.0, function() {
                    $(newrow).effect("pulsate", { times : 1 }, "slow", function () {
                        $(newrow).toggleClass("new-torrent-row");
                        stripeTable();
                        loadRClickMenus()
                    });
                });
            });
        },
        error : function (jqXHR, textStatus, errorThrown) {
            alert("Error " + jqXHR + " (" + errorThrown + ")");
        }
    });
}

function select_torrent(elem) {
     // elem.style.backgroundColor = "#00CCFF";
     if ((SELECTED.indexOf(elem.id) !== -1) && (SHIFT_SELECTED)) {
          elem.style.backgroundColor = "#fe0701";
     }
}
function deselect_torrent(elem) {
     if (SELECTED.indexOf(elem.id) !== -1) {
          elem.style.backgroundColor = "#7ae41b";
     }
}

function navigate_tab(elem) {
    window.location = "?view=" + elem.id.split("tab_")[1];
}

function navigate_tab_fromRSS(elem) {
     window.location = "/?view=" + elem.id.split("tab_")[1];
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
