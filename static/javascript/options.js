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

var tabView = null;

$(document).ready( function () {
   $("#tab_main").bind(
      "click",
      function () {
         window.location = "/?view=main";
      }
   );
   
   // check for hash fragment
   if (window.location.hash) {
      showoptions(window.location.hash.substring(1).split("show-")[1]);
   } else {
      showoptions("pyrt");
   }
   
   $("ol.sidebar-list > li").bind(
      "click", function (e) {
         nam = e.target.id.split("-tab")[0]
         showoptions(nam);
      }
   )
   $("input").bind("keyup", function (e) {
      if (e.target.id == "pyrt-newpass" || e.target.id == "pyrt-newpassconf") {
         //if ($("#pyrt-newpass").attr("value") == "" || $("#pyrt-newpassconf").attr("value") == "") {
         //   $("#pyrt-newpassconf,#pyrt-newpass").removeClass("badinput goodinput");
         //   return;
         //}
         //if ($("#pyrt-newpass").attr("value") == $("#pyrt-newpassconf").attr("value")) {
         //   $("#pyrt-newpassconf,#pyrt-newpass").removeClass("badinput").addClass("goodinput");
         //} else {
         //   $("#pyrt-newpassconf").addClass("badinput").removeClass("goodinput");
         //}
      } else if (e.target.id == "pyrt-oldpass") {
      } else if (e.target.value == "") {
         $(e.target).removeClass("badinput goodinput warninginput");
         $("#" + e.target.id + "error").html("");
      } else {
         verify(e.target.id, e.target.value);
      }
   }).bind("change", function (e) {
      if (e.target.id == "general-movecheck") {
         $(e.target).addClass("goodinput");
         if (e.target.checked == true) {
            $(".general-moveto").show();
         } else {
            $(".general-moveto").hide();
         }
      } else if (e.target.id == "general-stopcheck") {
         if (e.target.checked == true) {
            $("#general-stopat-parent").removeClass("hidden");
         } else {
            $("#general-stopat-parent").addClass("hidden");
         }
      } else if (e.target.value == "") {
         $(e.target).removeClass("badinput goodinput warninginput");
      }
   });
   $(".submit-box").bind("click", function (e) {
      elems = $("." + e.target.id.split("-")[0] + "-config.goodinput");
      keys = new Array();
      values = new Array();
      for (i=0;i<elems.length;i++) {
         keys.push(elems[i].id);
         if (elems[i].id == "general-movecheck") {
            values.push(encodeURIComponent(elems[i].checked));
         } else {
            values.push(encodeURIComponent(elems[i].value));
         }
      }
      if (keys.length > 0) {
         $.ajax({
            url: "/ajax?request=set_config_multiple&keys=" + keys + "&values=" + encodeURIComponent(values),
            success: function (data) {
               //$("#" + e.target.id.split("-")[0] + "-status").html(data);
               refresh_page();
            }
         });
      } else {
         alert("Nothing to submit!");
      }
   });
});

function dragstart(e) {
   e.dataTransfer.effectAllowed = "copy";
   e.dataTransfer.setData("Text", $(e.target).html());
   $("#tracker-info").html("Drag here to create a new group");
}

function dragover(e) {
   e.preventDefault();
}

function drop(e) {
   e.preventDefault();
   var realtarget = $(e.target).closest(".tracker-div");
   var data = e.dataTransfer.getData("Text");
   //console.log("Dropped on " + realtarget.attr("id") + ", with data: " + data);
   $.ajax({
      url: "/ajax?request=move_tracker&url=" + data + "&target_alias=" + realtarget.attr("id").split("tracker-")[1],
      success: function (data) {
         if (data == "OK") {
            refresh_page();
         } else {
            console.log(data);
         }
      }
   });
}

function dragend(e) {
   $("#tracker-info").html("Drag to group icons");
}

function dragoverInfo(e) {
   e.preventDefault();
   $(e.target).css({
      "color": "orange",
      "font-weight": "bold"
   });
}

function dragleaveInfo(e) {
   e.preventDefault();
   $(e.target).css({
      "color": "",
      "font-weight": ""
   });
}

function dropInfo(e) {
   e.preventDefault();
   console.log("Dropped into info box");
   $(e.target).css({
      "color": "",
      "font-weight": ""
   });
   var data = e.dataTransfer.getData("Text");
   $.ajax({
      url: "/ajax?request=move_tracker&url=" + data + "&target_alias=" + null,
      success: function (data) {
         if (data == "OK") {
            refresh_page();
         } else {
            console.log(data);
         }
      }
   })
}

function showoptions(nam) {
   $(".selected").each(function () {
      if (this.id !== "tab_options") {
         $(this).removeClass("selected");
      }
   })

   var tabs = ["pyrt","general","throttle","network","performance","trackers"]; 
   if (tabs.indexOf(nam) == -1) {
      nam = "pyrt";
   }
   
   tabView = nam;
   $("#" + nam + "-tab").addClass("selected");
   $("#" + nam).parent().addClass("selected");
}

function verify(key, value) {
   $.ajax({
      url: "/ajax?request=verify_conf_value&key=" + key + "&value=" + encodeURIComponent(value),
      success: function (data) {
         verif = data.substr(0,8);
         respo = data.substr(9,2);
         msg = data.substr(12);
         console.log(data)
         if (verif === "RESPONSE" && respo == "OK") {
            $("#" + key).removeClass("badinput warninginput").addClass("goodinput");
            $("#" + key + "error").html("");
         } else if (verif === "RESPONSE" && respo == "NO") {
            console.log($("#" + key));
            $("#" + key).removeClass("goodinput warninginput").addClass("badinput");
            $("#" + key + "error").html(msg);
         } else {
            $("#" + key).removeClass("goodinput badinput").addClass("warninginput");
            $("#" + key + "error").html("Unexpected response: " + data)
         }
      }
   })
   return false;
}

function refresh_page() {
   window.location.hash = "show-" + tabView;
   window.location.reload(window.location);
}