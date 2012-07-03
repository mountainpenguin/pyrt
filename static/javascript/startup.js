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
}

function progressEvent(e) {
    console.log("progress", e);
}

function noupdateEvent(e) {
    console.log("everything is up-to-date");
}

var appCache = document.getElementById("manifest-hack").applicationCache;
appCache.addEventListener("checking", checkingEvent, false);
appCache.addEventListener("downloading", downloadingEvent, false);
appCache.addEventListener("progress", progressEvent, false);
appCache.addEventListener("noupdate", noupdateEvent, false);