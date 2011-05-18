// function show_contents(elem) {
    // children = elem.children;
    // for (i=0; i<children.length; i++) {
        // if (children[i].tagName == "SPAN" || children[i].tagName == "IMG") {
            // children[i].style.display="inline";
        // } else {
            // children[i].style.display="block";
            // children[i].style.paddingLeft = "1em";
        // }
    // }
// }

$(document).ready(function () {
    $("#files_list").treeview({
        collapsed : true,
    });
    $(".file_document").each( function (index) {
        $(this).bind (
            "click",
            function () {
                read_elem($(this));
            }
        );
    });
});

function read_elem(elem) {
    alert(elem.innerHTML);
}