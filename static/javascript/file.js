var popupStatus = 0;

$(document).ready(function () {
    $("#files_list").treeview({
        collapsed : true,
    });
    $(".file_document").each( function (index) {
        $(this).bind (
            "mouseenter",
            function () {
                $(this).css({
                    "color" : "blue",
                    "cursor" : "pointer"
                })
            }
        );
        $(this).bind (
            "mouseleave",
            function () {
                $(this).css({
                    "color" : "inherit",
                    "cursor" : "inherit"
                })
            }
        );
        $(this).bind (
            "click",
            function () {
                loadContents($(this));
            }
        );
    });
    $("#popupContactClose").click( function () {
        disablePopup();
    });
    $("#backgroundPopup").click( function() {
        disablePopup();
    });
});

function loadContents(item) {
    $.ajax({
        url : "/ajax?request=get_file&filepath=" + encodeURIComponent(item.find(".fullpath").html()) + "&torrent_id=" + $("#torrent_id").html(),
        success : function(data) {
            $("#fileName").html(item.html());
            $("#contactArea").html("<pre><code>" + data + "</code></pre>")
            centerPopup();
            loadPopup();
        },
        statusCode : {
            500 : function () {
                alert("Server error");
            }
        }
        
    });
};
/* shamelessly copied from http://yensdesign.com/2008/09/how-to-create-a-stunning-and-smooth-popup-using-jquery/ */

function loadPopup() {
    if (popupStatus == 0) {
        $("#backgroundPopup").css({
            "opacity" : "0.7"
        });
        $("#backgroundPopup").fadeIn("slow");
        $("#popupContact").fadeIn("slow");
        popupStatus = 1;
    };
};

function disablePopup() {
    if (popupStatus == 1) {
        $("#backgroundPopup").fadeOut("slow");
        $("#popupContact").fadeOut("slow");
        popupStatus = 0;
    };
};

function centerPopup() {
    var windowWidth = document.documentElement.clientWidth;  
    var windowHeight = document.documentElement.clientHeight;  
    var popupHeight = $("#popupContact").height();  
    var popupWidth = $("#popupContact").width();  
    $("#popupContact").css({
        "position" : "absolute",
        "top" : (windowHeight-popupHeight)/2,
        "left" : (windowWidth-popupWidth)/2,
    });
};

/* end shameless copy */