function show_contents(elem) {
    elem.onclick = function () {
        hide_contents();
    }
    children = elem.children;
    for (i=0; i<children.length; i++) {
        if (children[i].tagName == "SPAN" || children[i].tagName == "IMG") {
            children[i].style.display="inline";
        } else {
            children[i].style.display="block";
            children[i].style.paddingLeft = "1em";
        }
    }
}

function hide_contents(elem) {
    alert("hide called!")
}