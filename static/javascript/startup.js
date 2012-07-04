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

function checkingEvent(e) {
    console.log("checking application cache");
}

function downloadingEvent(e) {
    console.log("there are new resources");
    var overlay = $("<p id='cacheupdate' />").css({
        "background-color" : "black",
        "z-index" : 200,
        "position": "fixed",
        "top": 0,
        "left" : 0,
        "width" : "100%",
        "height" : "100%"
    });
    $("body", window.parent.document).css({"overflow":"hidden","position":"fixed"}).prepend(overlay);
}

function progressEvent(e) {
    console.log("progress", e);
}

function noupdateEvent(e) {
    console.log("everything is up-to-date");
}

function updatereadyEvent(e) {
    console.log("got everything, should refresh now");
}

var appCache = window.applicationCache;
appCache.onchecking = checkingEvent;
appCache.ondownloading = downloadingEvent;
appCache.onprogress = progressEvent;
appCache.onnoupdate = noupdateEvent;
appCache.onupdateready = updatereadyEvent;
//appCache.addEventListener("downloading", downloadingEvent, false);