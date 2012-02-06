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
   $("input").bind("keyup", function (e) {
      if (e.target.id == "newpass" || e.target.id == "newpassconf") {
         if ($("#newpass").attr("value") == $("#newpassconf").attr("value")) {
            $("#newpassconf").removeClass("badinput");
         } else {
            $("#newpassconf").addClass("badinput");
         }
      } else if (e.target.value == "") {
         $(e.target).removeClass("badinput goodinput warninginput");
      } else {
         verify(e.target.id, e.target.value);
      }
   }).bind("change", function (e) {
      console.log("<" + e.target.value + ">");
      if (e.target.id == "network-movecheck") {
         if (e.target.checked == true) {
            $(".network-moveto").show();
         } else {
            $(".network-moveto").hide();
         }
      } else if (e.target.value == "") {
         $(e.target).removeClass("badinput goodinput warninginput");
      }
   });
});

function verify(key, value) {
   console.log(key + " changed to " + value + "!");
   $.ajax({
      url: "/ajax?request=verify_conf_value&key=" + key + "&value=" + encodeURIComponent(value),
      success: function (data) {
         verif = data.substr(0,8);
         respo = data.substr(9,2);
         msg = data.substr(12);
         if (verif === "RESPONSE" && respo == "OK") {
            $("#" + key).removeClass("badinput warninginput").addClass("goodinput").attr("title","");
         } else if (verif === "RESPONSE" && respo == "NO") {
            $("#" + key).removeClass("goodinput warninginput").addClass("badinput").attr("title", msg);
         } else {
            $("#" + key).removeClass("goodinput badinput").addClass("warninginput").attr("title", "Unexpected response: " + data);
         }
      }
   })
   return false;
}