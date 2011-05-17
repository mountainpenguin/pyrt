window.onload = function () {
    var files_div = document.getElementById("files_list");
    docroot = files_div.children[0]
    process_children(docroot);
    
}


function process_children(elem) {
    if (elem.hasChildren) {
        children = elem.children
        for (index=0; index<children.length; index++) {
            child = children[child]
            child.style.color = "red";
            // child.style.display = "none";
            if (child.className == "directory" && child.tagName == "div") {
                child.addEventListener("click", function () {
                    show_contents(child);
                });
                process_children(child);
            }
            child.style.color = null;
        }
    }
}

function show_contents(elem) {
    alert("Show Files!");
}