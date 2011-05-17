function show_contents(elem) {
    children = elem.children;
    for (i=0; i<children.length; i++) {
        children[i].style.display="block";
    }
}