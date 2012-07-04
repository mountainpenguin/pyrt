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

function downloadingEvent(e) {
    console.log("there are new resources");
    var overlay = $("<p id='cacheupdate' />").addClass('overlay');
    var inner = $("<div id='innerdiv' />").html(
        "A new version of PyRT is downloading"
    )
    overlay.append(inner);
    $("body", window.parent.document).css({"overflow":"hidden","position":"fixed"}).prepend(overlay);
}

function updatereadyEvent(e) {
    console.log("got everything, should refresh now");
    $("#innerdiv", window.parent.document).html(
        "A new version of PyRT is available, click <a href='/' alt='Refresh' title='Refresh'>here</a> to load it"
    )
}

var appCache = window.applicationCache;
appCache.ondownloading = downloadingEvent;
appCache.onupdateready = updatereadyEvent;
//appCache.addEventListener("downloading", downloadingEvent, false);