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
      if (e.target.id == "pyrt-newpass" || e.target.id == "pyrt-newpassconf") {
         if ($("#pyrt-newpass").attr("value") == "" || $("#pyrt-newpassconf").attr("value") == "") {
            $("#pyrt-newpassconf,#pyrt-newpass").removeClass("badinput goodinput");
            return;
         }
         if ($("#pyrt-newpass").attr("value") == $("#pyrt-newpassconf").attr("value")) {
            $("#pyrt-newpassconf,#pyrt-newpass").removeClass("badinput").addClass("goodinput");
         } else {
            $("#pyrt-newpassconf").addClass("badinput").removeClass("goodinput");
         }
      } else if (e.target.value == "") {
         $(e.target).removeClass("badinput goodinput warninginput");
         $("#" + e.target.id + "error").html("");
      } else {
         verify(e.target.id, e.target.value);
      }
   }).bind("change", function (e) {
      if (e.target.id == "general-movecheck") {
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
      console.log("Submitting <" + e.target.id.split("-")[0] + ">");
      elems = $("." + e.target.id.split("-")[0] + "-config.goodinput");
      console.log("." + e.target.id.split("-")[0] + "-config.goodinput");
      keys = new Array();
      values = new Array();
      for (i=0;i<elems.length;i++) {
         keys.push(elems[i].id);
         values.push(encodeURIComponent(elems[i].value));
      }
      console.log("keys: " + keys);
      $.ajax({
         url: "/ajax?request=set_config_multiple&keys=" + keys + "&values=" + encodeURIComponent(values),
         success: function (data) {
            console.log(data);
            $("#" + e.target.id.split("-")[0] + "-status").html(data);
         }
      });
   });
});

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