var popupStatus = 0;

$(document).ready(function () {
    $("#files_list").treeview({
        collapsed : true,
    });
    $(".file_document").each( function (index) {
        $(this).bind (
            "click",
            function () {
                loadPopup();
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
        "top" : windowHeight/2-popupHeight/2,
        "left" : windowWidth/2-popupWidth/2,
        "height" : windowHeight
    });
};

/* end shameless copy */