var rtorrent_display = false;
var pyrt_display = false;

$(document).ready( function () {
   $("#slide-me").hide("slide", { direction : "left" }, 1000, function () {
      $("#tab_pyrt").show("slide", { direction : "left" }, 500);
      $("#tab_rtorrent").show("slide", { direction : "left" }, 500);
   });
   $("#tab_main").bind(
      "click",
      function () {
       window.location = "/?view=main";
      }
   );
   $("#tab_pyrt").bind(
      "click",
      function () {
         if (rtorrent_display) {
            $("#rtorrent-options-wrapper").hide("slide", { direction : "up" }, 500, function () {
               $("#pyrt-options-wrapper").show("slide", { direction : "up" }, 500);
            });
         } else if (pyrt_display) {
         } else {
            $("#pyrt-options-wrapper").show("slide", { direction : "up" }, 500);
         }
         pyrt_display = (function () {
            $("#tab_pyrt").addClass("hover");
            return true;
         })();
         rtorrent_display = (function () {
            $("#tab_rtorrent").removeClass("hover");
            return false;
         })();
      }
   );
   $("#tab_rtorrent").bind(
      "click",
      function () {
         if (pyrt_display) {
            $("#pyrt-options-wrapper").hide("slide", { direction : "up" }, 500, function () {
               $("#rtorrent-options-wrapper").show("slide", { direction : "up" }, 500);
            });
         } else if (rtorrent_display) {
         } else {
            $("#rtorrent-options-wrapper").show("slide", { direction : "up" }, 500);
         }
         pyrt_display = (function () {
            $("#tab_pyrt").removeClass("hover");
            return false;
         })();
         rtorrent_display = (function () {
            $("#tab_rtorrent").addClass("hover");
            return true;
         })();
      }
   );
   $("#pyrt-newpw_confirm-input").bind(
      "change",
      function () {
         pw1 = $("#pyrt-newpw-input").val();
         pw2 = $(this).val();
         if (pw1 !== pw2) {
            $("#pyrt-newpw_report-span").html(
               "X" 
            ).removeClass("ok").addClass("bad");
         } else {
            $("#pyrt-newpw_report-span").html(
               ":)"
            ).removeClass("bad").addClass("ok");
         }
      }
   );
});

function select_tab(elem) {
   $(elem).addClass("hover_temp");
}

function deselect_tab(elem) {
   $(elem).removeClass("hover_temp");
}