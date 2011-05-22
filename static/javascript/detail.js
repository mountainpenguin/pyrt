function select(elem) {
    elem.style.backgroundColor = "#37FDFC";
}
function deselect(elem) {
    elem.style.backgroundColor = null;
}
function navigate(elem) {
    window.location = "?torrent_id=" + document.URL.split("?torrent_id=")[1].split("&")[0] + "&view=" + elem.id;
}
function navigate_home() {
    window.location = "/index";
}

$(document).ready(function (){
	$("#accordion").accordion();
});

$(document).ready(function () {
    $("#files_list").treeview({
        collapsed : true,
    });
});