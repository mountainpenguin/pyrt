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
   elem.style.backgroundColor = "#37FDFC"; 
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
    new_html += "<div class='column-1'>Downloaded:</div><div class='column-2'>" + obj.downloaded  + "</div>"
    new_html += "<div class='column-1'>Uploaded:</div><div class='column-2'>" + obj.uploaded + "</div>"
    new_html += "<div class='column-1'>Ratio:</div><div class='column-2'>" + obj.ratio + "</div>"
    new_html += "<div class='column-1'>Peers:</div><div class='column-2'>" + obj.peers.length + "</div>"
    new_html += "<div class='column-1'>Created:</div><div class='column-2'>" + obj.created + "</div>"
    new_html += "<div class='column-2' style='clear : left;'><span class='fakelink' onClick='removerow(\"" + obj.torrent_id + "\")'>Close</span> <a href='detail?torrent_id=" + obj.torrent_id + "'>Detailed View</a></div>"
    new_html += "</div>"
    cell.innerHTML = new_html;
    cell.style.borderLeft="1px dotted";
    cell.style.borderRight="1px dotted";
    cell.style.backgroundColor = "white";
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
    if (cmd === "pause_torrent" || cmd === "start_torrent" || cmd === "stop_torrent" || cmd == "remove_torrent" || cmd == "delete_torrent") {
        var resp;
        if (cmd === "remove_torrent") {
            resp = confirm("Are you sure you want to remove this torrent?")
        } else if (cmd == "delete_torrent") {
            resp = confirm("Are you sure you want to remove this torrent and *permanently* delete its files?")
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

function _remove_add_dialogue() {
    var parent = document.getElementById("add_torrent")
    var children = parent.children;
    var remove = new Array();
    for (i=0; i<children.length; i++) {
        if (children[i].id != "add_img") {
            remove.push(children[i]);
        }
    }
    for (i=0; i<remove.length; i++) {
        parent.removeChild(remove[i]);
    }
}
function show_add_dialogue(elem) {
    if (!(document.getElementById("add_torrent_input"))) {
        var addSpan = document.createElement("span");
        addSpan.id = "add_text";
        addSpan.className = "add_torrent_button";
        addSpan.innerHTML = "Add torrent";
        addSpan.addEventListener("click", function () {
            add_torrent();
        });
        addSpan.addEventListener("mouseover", function () {
            addSpan.style.color = "blue";
        });
        addSpan.addEventListener("mouseout", function () {
            addSpan.style.color = null;
        });
        elem.appendChild(addSpan);
        
        var cancelSpan = document.createElement("span");
        cancelSpan.id = "cancel_add";
        cancelSpan.className = "add_torrent_button";
        cancelSpan.innerHTML = "Cancel";
        cancelSpan.addEventListener("click", function () {
            _remove_add_dialogue();
        });
        cancelSpan.addEventListener("mouseover", function () {
            cancelSpan.style.color = "blue";
        });
        cancelSpan.addEventListener("mouseout", function () {
            cancelSpan.style.color = null;
        });
        elem.appendChild(cancelSpan);
        
        var form = document.createElement("form");
        form.id = "add_torrent_form";
        form.action = "upload_torrent";
        form.method = "post";
        form.enctype = "multipart/form-data";
        
        var startCheckText = document.createElement("div");
        startCheckText.className = "add_torrent_start_text";
        startCheckText.innerHTML = "Start Immediately? ";
        
        var startCheck = document.createElement("input");
        startCheck.id = "add_torrent_start";
        startCheck.type = "checkbox";
        startCheck.checked = "checked";
        startCheck.name = "start";
        
        startCheckText.appendChild(startCheck);
        form.appendChild(startCheckText);
        
        var fileInput = document.createElement("input");
        fileInput.id = "add_torrent_input";
        fileInput.accept = "application/x-bittorrent";
        fileInput.type = "file";
        fileInput.name = "torrent";
        form.appendChild(fileInput);
        
        elem.appendChild(form);
    }
}

function add_torrent() {
    var add_torrent = document.getElementById("add_torrent_input")
    if (!(add_torrent.value)) {
        add_torrent.style.border = "1px solid red";
    } else {
        var form = document.getElementById("add_torrent_form");
        form.submit();
    }
}