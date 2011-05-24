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
            $("#rtorrent-options-wrapper").hide("slide", { direction : "down" }, 500, function () {
               $("#pyrt-options-wrapper").show("slide", { direction : "up" }, 500);
            });
         } else {
            $("#pyrt-options-wrapper").show("slide", { direction : "up" }, 500);
         }
         pyrt_display = true;
         rtorrent_display = false;
      }
   );
   $("#tab_rtorrent").bind(
      "click",
      function () {
         if (pyrt_display) {
            $("#pyrt-options-wrapper").hide("slide", { direction : "down" }, 500, function () {
               $("#rtorrent-options-wrapper").show("slide", { direction : "up" }, 500);
            });
         } else {
            $("#rtorrent-options-wrapper").show("slide", { direction : "up" }, 500);
         }
         pyrt_display = false;
         rtorrent_display = true;
      }
   );
});

function select_tab(elem) {
   $(elem).addClass("hover");
}

function deselect_tab(elem) {
   $(elem).removeClass("hover");
}