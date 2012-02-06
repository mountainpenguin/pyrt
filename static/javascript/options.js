var rtorrent_display = false;
var pyrt_display = false;

$(document).ready( function () {
   $("#tab_main").bind(
      "click",
      function () {
         window.location = "/?view=main";
      }
   );
   $("ol.sidebar-list > li").bind(
      "click", function (e) {
         $(".selected").each(function () {
            if (this.id !== "tab_options") {
               $(this).removeClass("selected");
            }
         })
         $(e.target).addClass("selected");
         $("#" + e.target.id.split("-tab")[0]).parent().addClass("selected");
      }
   )
   $("input").bind("change", function (e) {
      if (e.target.id == "network-movecheck") {
         if (e.target.checked == true) {
            $(".network-moveto").show();
         } else {
            $(".network-moveto").hide();
         }
      }
   });
});