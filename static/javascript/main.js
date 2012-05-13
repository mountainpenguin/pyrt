var CTRL_SELECTED = false;
var SELECTED = new Array();
var statusArrayInactive = new Array("Stopped","Paused");
var statusArrayActive = new Array("Seeding (idle)", "Seeding", "Leeching (idle)", "Leeching", "Hashing");
var DELETING = new Array();
var DROP_OPEN = new Array();
var ws = null;
var dragOverlayOpen = null;
var dragOverlayCreated = null;
if (window.document.location.protocol == "https:") {
     var socket_protocol = "wss"
} else {
     var socket_protocol = "ws"
}

$(document).ready(function () {
     setTimeout(function () {
          refresh_content("yes");
     }, 5000);

     ws = new window.WebSocket(socket_protocol + "://" + window.document.location.host + "/ajaxsocket");
     ws.onmessage = function(e) {
     }
     ws.onclose = function(e) {
     }
     ws.onopen = function(e) {
     }
     ws.onerror = function(e) {
        console.log("WebSocket error", ws, e);
     }
     
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
     
     // drag 'n' drop events
     $("body").bind("dragenter", function (e) {
          
          if ( (new Date()).getTime() - dragOverlayCreated > 500 ) {
               createDragOverlay();
          }
          e.preventDefault();
          e.stopPropagation();
          return false;
     }).bind("dragleave", function (e) {
          if ( (new Date()).getTime() - dragOverlayCreated > 500 ) {
               destroyDragOverlay();
          }
          e.preventDefault();
          e.stopPropagation();
          return false
     
     }).bind("drop", function (e) {
          //destroyDragOverlay();
          var files = e.originalEvent.dataTransfer.files;
          if (files.length > 0) {
               fs = new window.WebSocket(socket_protocol + "://" + window.document.location.host + "/filesocket");
               fs.onmessage = function(ev) {
                    // format json: filename: <filename>, response: <response>
                    resp = JSON.parse(ev.data);
                    console.log("fileSocket response parsed", resp)
               }
               fs.onclose = function(ev) {
               }
               fs.onopen = function(ev) {
                    for (i=0; i<files.length; i++) {
                         if (files[i].type == "application/x-bittorrent") {
                              console.log(files[i]);
                              var randid = Math.random().toString(36).substr(2, 5)
                              $("<div id='dragOverlayDialog-file-" + randid + "'>").addClass("dragOverlayDialog-file-ok").html("<span class='dragOverlayDialog-filename'>" + files[i].name + "</span> uploaded").appendTo("#dragOverlayDialog");
                              var reader = new FileReader();
                              var filename = files[i].name;
                              
                              reader.onload = function (eve) {
                                   fs.send("FILENAME@@@" + filename + ":::ID@@@" + randid + ":::CONTENT@@@" + eve.currentTarget.result);
                              }
                              reader.onerror = function (eve) {
                              }
                              reader.readAsBinaryString(files[i]);
                         } else {
                              $("<div />").addClass("dragOverlayDialog-file-bad").html(files[i].name + " ignored").appendTo("#dragOverlayDialog");
                         }
                    }
                    //fs.close();
               }
               fs.onerror = function(e) {
                  console.log("WebSocket error", ws, e);
               }
          } else {
               destroyDragOverlay();
          }
          
          e.originalEvent.preventDefault();
          e.originalEvent.stopPropagation();
          e.preventDefault();
          e.stopPropagation();
          return false;
     });
     
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
     
     $(".torrent-div").live("click", function (e) {
          if ($(e.target).is("img")) {
               return;
          }
          if (e.ctrlKey) {
          } else {
               torrent_id = $(e.target).parent().attr("id").split("torrent_id_")[1];
               if ($.inArray(torrent_id, DROP_OPEN) == -1) {
                    drop_down(this);
               } else {
                    drop_up(torrent_id);
               }
          }
     });
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
          sendme = "request=" + action + "_batch";
          sendme = sendme + "&torrentIDs=" + torrentIDs.join(",");
          ws.onmessage = function (e) { };
          ws.send(sendme)
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
     });
     $(".control_start_me").live("click", function (event) {
          torrent_id = $(this).parents(".torrent-div").attr("id").split("torrent_id_")[1];
          command("start_torrent", torrent_id);
          return false;
     });
     $(".control_pause_me").live("click", function (event, ui) {
          torrent_id = $(this).parents(".torrent-div").attr("id").split("torrent_id_")[1];
          command("pause_torrent", torrent_id);
          return false;
     });
     $(".control_stop_me").live("click", function (event) {
          torrent_id = $(this).parents(".torrent-div").attr("id").split("torrent_id_")[1];
          command("stop_torrent", torrent_id);
          return false;
     });
     $(".control_remove_me").live("click", function (event) {
          torrent_id = $(this).parents(".torrent-div").attr("id").split("torrent_id_")[1];
          command("remove_torrent", torrent_id);
          return false;
     });
     $(".control_delete_me").live("click", function (event) {
          torrent_id = $(this).parents(".torrent-div").attr("id").split("torrent_id_")[1];
          command("delete_torrent", torrent_id);
          return false; 
     });
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
         window.location = "/options";
         }
     );
     $("#tab_rss").bind(
         "click",
         function () {
           window.location = "/RSS";
         }
     );
}

function parse_content(e, repeat) {
     ws.onmessage = function () {};
     data = JSON.parse(e.data);
       system = JSON.parse(data.system);
       $("#global_uprate").html(system.uprate + "/s");
       $("#global_uptot").html(system.uptot);
       $("#global_diskusage").html(system.diskused + " / " + system.disktotal);
       $("#global_downrate").html(system.downrate + "/s");
       $("#global_downtot").html(system.downtot);
       $("#global_memusage").html(system.memused + " / " + system.memtotal);
       $("#global_load1").html(system.load1);
       $("#global_load5").html(system.load5);
       $("#global_load15").html(system.load15);
       $("#global_uptime").html(system.uptime);
       $("#global_cpuusage").html(system.cpuusage + "%");
       
     // data has structure:
         //{
         //    "torrents" : {},
         //    "system" : system_html,
         //    "torrent_index" : [id, id, id] // this is in the order that they are arranged in the page (or should be if this has changed)
         //}
     torrent_list = $("#torrent_list").find($("tr.torrent-div"))
     
     cur_t_ids = new Array();
     
     if ((DROP_OPEN.length > 0) && (data.drop_down_keys.length > 0)) {
         for (i=0; i<DROP_OPEN.length; i++) {
            tid = DROP_OPEN[i];
            if (data.drop_down_keys.indexOf(tid) !== -1) {
                 htmldata = data.drop_downs[tid];
                 cur_pane = 1;
                 $("#drop_down_container_" + tid).find(".slide").each(function(i, elem) {
                      if ($(elem).find("h2.selected").length !== 0) {
                           cur_pane = i + 1;
                      }
                 });
                 htmldata = accordionise($(htmldata), cur_pane);
                 htmldata = filetreeise($(htmldata), tid);
                 $("#newrow_torrent_id_" + tid + " > td").html(htmldata);
            }
         }
     }
     
     for (i=0; i<torrent_list.length; i++) {
         var torrent_id = $(torrent_list[i]).attr("id").split("torrent_id_")[1];
         cur_t_ids.push(torrent_id);
         if (data.torrent_index.indexOf(torrent_id) == -1) {
            if ($("#torrent_id_" + torrent_id).hasClass("old-torrent-row")) {} else {
                 if (DEL_INDEX = DELETING.indexOf(torrent_id) != -1) {
                      DELETING.splice(DEL_INDEX, 1);
                 }
                 remove_torrentrow(torrent_id)
            }
         } else {
             // refresh torrent data
             torrent_data = data.torrents[torrent_id];
             
             if (torrent_data.completed) {
                 $("#t_name_" + torrent_id).removeClass("progress-gradient")
             } else {
                 $("#t_name_" + torrent_id).addClass("progress-gradient").css({
                      "background-size" : torrent_data.percentage + "% 100%, 100% 100%",
                 })
             }
            
             $("#t_ratio_" + torrent_id).html(torrent_data.ratio).attr("title",torrent_data.up_total + " up / " + torrent_data.down_total + " down");
             $("#t_uprate_" + torrent_id).html(torrent_data.uprate + "/s");
             $("#t_downrate_" + torrent_id).html(torrent_data.downrate + "/s");
             var oldstatuselem = $("#t_status_" + torrent_id);
             var oldstatus = oldstatuselem.html()
             if (oldstatus != torrent_data.status) {
                 oldstatuselem.html(torrent_data.status);
                 // update buttons
                 if ( ( $.inArray(oldstatus, statusArrayActive) != -1 ) && ( $.inArray(torrent_data.status, statusArrayInactive) != -1 ) ) {
                      $("#t_controls_" + torrent_id + " > .control_pause").replaceWith(
                           $("<span />").addClass("control_start control_button")
                                        .attr("title", "Start Torrent")
                                        .append(
                                           $("<img />").addClass("control_image control_start_me")
                                            .attr("alt", "Start").attr("src","../images/start.png")
                                        )
                      );
                      $("#torrent_id_" + torrent_id).toggleClass("rcpause rcstart");
                      loadRClickMenus();
                 
                 } else if ( ( $.inArray(oldstatus, statusArrayInactive) != -1 ) && ( $.inArray(torrent_data.status, statusArrayActive) != -1 ) ) {
                      $("#t_controls_" + torrent_id + " > .control_start").replaceWith(
                           $("<span />").addClass("control_pause control_button")
                                        .attr("title", "Pause Torrent")
                                        .append(
                                           $("<img />").addClass("control_image control_pause_me")
                                            .attr("alt", "Pause").attr("src","../images/pause.png")
                                        )
                      )
                      $("#torrent_id_" + torrent_id).toggleClass("rcpause rcstart");
                 }
             }
             
         }
     }
       
     // check for new torrents and add them
     for (i=0; i<data.torrent_index.length; i++) {
         torrent_id = data.torrent_index[i];
         if ($.inArray(torrent_id, cur_t_ids) === -1) {
             add_torrentrow(torrent_id, data.torrents[torrent_id], i)
         }
     }
     
     stripeTable();
     loadRClickMenus();

     if (repeat === "yes") {
         setTimeout(function () {
             refresh_content("yes");
         }, 5000);
     }
}

function refresh_content(repeat) {
    // get all torrent ids on page
    if (DROP_OPEN.length > 0) {
     req = "request=get_info_multi&view=" + $("#this_view").html() + "&drop_down_ids=" + DROP_OPEN.join(",") 
    } else {
     req = "request=get_info_multi&view=" + $("#this_view").html()
    }
    
    if (!($("#this_sort").html() === "none")) {
        req += "&sortby=" + $("#this_sort").html();
    }
    if (!($("#this_reverse").html() === "none")) {
        req += "&reverse=" + $("#this_reverse").html();
    }
    
/*    $.getJSON(req, function (data) { */
    ws.onmessage = function(e) { return parse_content(e, repeat) };
    ws.send(req);
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

function add_torrentrow(torrent_id, torrent_data, torrent_index) {
    var newrow = $("<tr />").addClass("torrent-div").attr("id","torrent_id_" + torrent_id);
    if (torrent_data.completed) {
          newrow.append($("<td />")
                        .attr("id", "t_name_" + torrent_id)
                        .addClass("t_name")
                        .html(torrent_data.name)
                        )
    } else {
          newrow.append($("<td />")
                        .attr("id","t_name_" + torrent_id)
                        .html(torrent_data.name)
                        .addClass("progress-gradient t_name")
                        .css("background-size", torrent_data.percentage + "%, auto")
                        )
    }
     newrow.append($("<td />")
                  .attr("id","t_size_" + torrent_id)
                  .html(torrent_data.size)
                  )
          .append($("<td />")
                  .attr("id","t_ratio_" + torrent_id)
                  .attr("title",torrent_data.up_total + " up / " + torrent_data.down_total + " down")
                  .html(torrent_data.ratio)
                  )
          .append($("<td />")
                  .attr("id", "t_uprate_" + torrent_id)
                  .html(torrent_data.uprate + "/s")
                  )
          .append($("<td />")
                  .attr("id", "t_downrate_" + torrent_id)
                  .html(torrent_data.downrate + "/s")
                  )
          .append($("<td />")
                  .attr("id", "t_status_" + torrent_id)
                  .html(torrent_data.status)
                  )
          .append($("<td />")
                  .attr("id", "t_controls_" + torrent_id)
                  .append($("<span />")
                         .addClass("control_stop control_button")
                         .attr("title", "Stop Torrent")
                         .append($("<img />")
                                 .addClass("control_image control_stop_me")
                                 .css("padding-right", "4px")
                                 .attr("alt", "Stop")
                                 .attr("src", "../images/stop.png")
                         )
                    )
                  .append($("<span />")
                         .addClass("control_remove control_button")
                         .attr("title", "Remove Torrent")
                         .append($("<img />")
                                 .addClass("control_image control_remove_me")
                                 .css("padding-right", "4px")
                                 .attr("alt", "Remove")
                                 .attr("src", "../images/remove.png")
                         )
                    )
                  .append($("<span />")
                         .addClass("control_delete control_button")
                         .attr("title", "Remove Torrent and Files")
                         .append($("<img />")
                                 .addClass("control_image control_delete_me")
                                 .css("padding-right", "4px")
                                 .attr("alt", "Delete")
                                 .attr("src", "../images/delete.png")
                         )
                    )
                  )

    if ($.inArray(torrent_data.status, statusArrayActive) != -1) {
          newrow.addClass("rcpause");
          newrow.find("td#t_controls_" + torrent_id).prepend($("<span />")
                                                             .addClass("control_pause control_button")
                                                             .attr("title", "Pause Torrent")
                                                             .append($("<img />")
                                                                     .addClass("control_image control_pause_me")
                                                                     .css("padding-right", "4px")
                                                                     .attr("alt", "Pause")
                                                                     .attr("src", "../images/pause.png")
                                                                     )
                                                             );
    } else {
          newrow.addClass("rcstart");
          newrow.find("td#t_controls_" + torrent_id).prepend($("<span />")
                                                             .addClass("control_start control_button")
                                                             .attr("title", "Start Torrent")
                                                             .append($("<img />")
                                                                     .addClass("control_image control_start_me")
                                                                     .css("padding-right", "4px")
                                                                     .attr("alt", "Start")
                                                                     .attr("src", "../images/start.png")
                                                                     )
                                                             );
    }
    
    
    $("#torrent_list > tbody > tr:eq(" + torrent_index + ")").after(newrow);
    
     //$("#torrent_id_" + torrent_id).slideRow("down", 1000, function () {
     //     $("#torrent_id_" + torrent_id).fadeTo(2000, 1.0, function() {
     //          $("#torrent_id_" + torrent_id).effect("pulsate", { times : 1 }, "slow", function () {
     //               $("#torrent_id_" + torrent_id).toggleClass("new-torrent-row");
     //               stripeTable();
     //          })
     //     })
     //});
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
function drop_down(elem) {
     var torrent_id = elem.id.split("torrent_id_")[1];
     DROP_OPEN.push(torrent_id);
     var table = document.getElementById("torrent_list");
     if (oldrow = document.getElementById('newrow_torrent_id_' + torrent_id)) {
          table.deleteRow(oldrow.rowIndex);
     }
     var newrow = table.insertRow(elem.rowIndex + 1);
     var newcell = newrow.insertCell(0);
     newrow.id = "newrow_torrent_id_" + torrent_id;
     newrow.className += "drop_down";
     newcell.innerHTML = "<img src='/images/loading.gif'> <span style='color:red;'>Loading</span>";
     newcell.colSpan = "7";
     var params = "request=get_torrent_info&html=yesplease&torrent_id=" + torrent_id;
     ws.onmessage = function (e) {
          var response = e.data;
          newcell.className += "drop_down_td";
          newcellcontents = $(response);
          newcellcontents = accordionise(newcellcontents, 1);
          newcellcontents = filetreeise(newcellcontents, torrent_id);
          newcellcontents.css({"display" : "none"});
          $(newcell).html(newcellcontents);
          newcellcontents.slideDown('slow');
     }
     ws.send(params)
}

function drop_up(t_id) {
     drop_index = DROP_OPEN.indexOf(torrent_id);
     DROP_OPEN.splice(drop_index, 1);
     $("#newrow_torrent_id_" + t_id + " > td > div").slideUp("slow", function () {
          $("#newrow_torrent_id_" + t_id).remove();
     })
     /*"slow", function() {
          $(this).remove();
     });*/
}

function accordionise(cell, curr_pane) {
     cell.liteAccordion({
          containerWidth : $(".torrent-div").first().width(),
          firstSlide : curr_pane
     });
     return cell;
}

function filetreeise(cell, torrent_id) {
     cell.find("#drop_down_files_" + torrent_id + " > ul").treeview({
          collapsed : true,
          persist: "cookie",
     });
     return cell;
}

function command(cmd, t_id) {
     if ($.inArray(t_id, DELETING) != -1) {
          return false;
     }
     if (cmd === "pause_torrent" || cmd === "start_torrent" || cmd === "stop_torrent" || cmd == "remove_torrent" || cmd == "delete_torrent" || cmd == "hash_torrent") {
          var resp;
          if (cmd === "remove_torrent") {
               resp = confirm("Are you sure you want to remove this torrent?");
          } else if (cmd == "delete_torrent") {
               resp = confirm("Are you sure you want to remove this torrent and *permanently* delete its files?");
               if (resp) {
                    $("#torrent_id_" + t_id).addClass("deleting-torrent-row").removeClass("blue green");
                    DELETING.push(t_id);
               }
          } else if (cmd == "hash_torrent") {
               resp = confirm("Are you sure you want to rehash this torrent?\n This process can take a long time for large torrents");
          } else {
               resp = true;
          }
          if (resp) {
               ws.onmessage = function (e) {
                    var resp = e.data.trim()
                    if (resp == "OK") {
                         refresh_content("no");
                    } else {
                         alert("Command Failed with reason: " + resp); 
                    }
               }
               var params = "request=" + cmd + "&torrent_id=" + t_id;
               ws.send(params);
     
          } else {
               return false;
          }
     } else {
          alert("invalid command or command not implemented");
     }
}

function createDragOverlay() {
     if (dragOverlayOpen) {
          return false;
     } else {
          dragOverlayCreated = (new Date()).getTime();
          dragOverlayOpen = true;
          var overlay = $("<div />").addClass("dragOverlay").appendTo("body");
          var overlaydialog = $("<div id='dragOverlayDialog' />").addClass("dragOverlayDialog").appendTo(overlay);
     }
}
function destroyDragOverlay() {
     if (dragOverlayOpen) {
          dragOverlayOpen = false;
          $(".dragOverlay").each( function (elem) {
               $(this).fadeOut(2000, function () {
                    $(this).remove()
               })
          });
     }
}
