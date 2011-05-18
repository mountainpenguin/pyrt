function show_contents(elem) {
    children = elem.children;
    for (i=0; i<children.length; i++) {
        alert(children[i].tagName);
        if (children[i].tagName == "span") {
            children[i].style.display="inline";
        } else {
            children[i].style.display="block";
            children[i].style.paddingLeft = "1em";
        }
    }
}