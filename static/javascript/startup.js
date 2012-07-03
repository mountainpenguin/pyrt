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
 
$(document).ready( function () {
    var appCache = window.applicationCache;
    
    $(appCache).bind("checking", function (e) {
        console.log("checking application cache");
    }).bind("downloading", function (e) {
        console.log("there are new resources");
    }).bind("progress", function(e) {
        console.log("progress", e);
    }).bind("noupdate", function(e) {
        console.log("everything up to date");
    });
    appCache.update();
});