/*  Copyright (C) 2012 by mountainpenguin (pinguino.de.montana@googlemail.com)
 *  http://github.com/mountainpenguin/pyrt
 *
 *  This file is part of pyRT.
 *  
 *  pyRT is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  pyRT is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with pyRT.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

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
    $("#files_list").treeview({
        collapsed : true
    });
    $("#accordion").accordion();
});