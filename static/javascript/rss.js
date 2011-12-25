$(document).ready(function () {
    getFeeds();
});

function select_tab(elem) {
   elem.style.backgroundColor = "#bbbbbb"; 
}

function deselect_tab(elem) {
    elem.style.backgroundColor = null;
}

function navigate_tab(elem) {
    window.location = "?view=" + elem.id.split("tab_")[1];
}

function navigate_tab_fromRSS(elem) {
     window.location = "/?view=" + elem.id.split("tab_")[1];
}

function getFeeds() {
    var feeds = $("#feed_wrapper");
    $.ajax({
       url : "/ajax?request=get_feeds",
       context : feeds,
       dataType : "html",
       success : function (data) {
        $(this).html(data);
       }
    });
}