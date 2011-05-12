var xmlhttp;

function select_torrent(elem) {
    elem.style.backgroundColor = "#37FDFC";
    elem.style.cursor = "help";
}
function deselect_torrent(elem) {
    elem.style.backgroundColor = null;
    elem.style.cursor = "default";
}

function htmlify(json, cell) {
    var obj = JSON.parse(json);
    var new_html = new String();
    new_html += "<div class='column-1'>ID:</div><div class='column-2'>" + obj.torrent_id + "</div>"
    new_html += "<div class='column-1'>Size:</div><div class='column-2'>" + obj.size + " MB</div>"
    new_html += "<div class='column-1'>Downloaded:</div><div class='column-2'>" + obj.downloaded  + " MB</div>"
    new_html += "<div class='column-1'>Uploaded:</div><div class='column-2'>" + obj.uploaded + " MB</div>"
    new_html += "<div class='column-1'>Ratio:</div><div class='column-2'>" + obj.ratio + "</div>"
    new_html += "<div class='column-1'>Peers:</div><div class='column-2'>" + obj.peers.length + "</div>"
    new_html += "<div class='column-1'>Created:</div><div class='column-2'>" + obj.created + "</div>"
    new_html += "<div class='column-2' style='clear : left;'><a href='detail.py?torrent_id=" + obj.torrent_id + "'>Detailed View</a></div>"

    cell.innerHTML = new_html;
}
function view_torrent(elem) {
    var torrent_id = elem.id.split("torrent_id_")[1];
    var table = document.getElementById("torrent_list");
    var newrow = table.insertRow(elem.rowIndex + 1);
    var newcell = newrow.insertCell(0);
    newcell.innerHTML = "<img src='http://mountainpenguin.org.uk/pyj/loading.gif'> <span style='color:red;'>Loading</span>";
    xmlhttp = new XMLHttpRequest();
    var url="ajax.py"
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
