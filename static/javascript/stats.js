var StatSocket = null;
var UpData = new Array();
var DownData = new Array();
var LoadData = new Array();
var MemData = new Array();
var netctx = null;
var sysctx = null;
var cHeight = null; // canvas total height (specified in HTML)
var cWidth = null; // canvas total width (specified in HTML)
var cOriginX = null; // bottom left of axes
var cOriginY = null; // bottom left of axes
var eHeight = null; // effective height (i.e. top of graph to bottom of axes)
var eWidth = null; // effective width (i.e. y-axis to left-most edge of graph)
var xoffset = 5; // distance between canvas left edge and y-axis
var yoffset = 6; // distance between canvas top edge and top of the y-axis
var nxoffset = 55; // distance between canvas right edge and end of x-axis
var nyoffset = 10; // distance between canvas bottom edge and x-axis
var maxValues = null;

if (window.document.location.protocol == "https:") {
     var socket_protocol = "wss"
} else {
     var socket_protocol = "ws"
}

$(document).ready(function() {
    StatSocket = new WebSocket(socket_protocol + "://" + window.document.location.host + "/statsocket");
    StatSocket.onmessage = onMessage;
    StatSocket.onopen = onOpen;
    StatSocket.onclose = onClose;
    StatSocket.onerror = onError;
});

function mainLoop() {
     StatSocket.send("request=global");
     setTimeout(mainLoop, 1000);
}

function initGraph() {
     cHeight = parseInt($("#canvas-net").height());
     cWidth = parseInt($("#canvas-net").width());
     
     cOriginX = xoffset;
     cOriginY = cHeight - nyoffset;
     eHeight = cOriginY - yoffset;
     eWidth = cWidth - xoffset - nxoffset;
     
     maxValues = Math.floor(eWidth / 2);
     
     clearCanvas($("#canvas-net"));
     var netcanvas = document.getElementById("canvas-net");
     netctx = netcanvas.getContext("2d");
     var syscanvas = document.getElementById("canvas-system");
     sysctx = syscanvas.getContext("2d");

     drawAxes(netctx);
     drawAxes(sysctx);
     drawLegend(netctx, new Array("Upload","Download"));
     drawLegend(sysctx, new Array("Load Avg"));
}

function _drawLegendItem(ctx, text, startX, startY, fillStyle) {
     ctx.fillStyle = fillStyle;
     ctx.beginPath();
     ctx.moveTo(startX, startY);
     ctx.lineTo(startX + (nxoffset-5), startY);
     ctx.lineTo(startX + (nxoffset-5), startY+10);
     ctx.lineTo(startX, startY+10);
     ctx.lineTo(startX, startY);
     ctx.fill();
     ctx.closePath();
     ctx.fillText(text, startX, startY + 20);

}
function drawLegend(ctx, leg_text) {
     styles = new Array(
         "rgb(255,0,0)",
         "rgb(0,0,255)",
         "rgb(0,255,0)"
     );
     for (i=0; i<leg_text.length; i++) {
         startX = cWidth - (nxoffset-5);
         startY = 30*(i+1) + xoffset;
         _drawLegendItem(ctx, leg_text[i], startX, startY, styles[i]);
     }
}

function drawAxes(ctx) {
     ctx.strokeStyle = "rgb(0,0,0)";
     ctx.fillStyle = "rgb(0,0,0)";
     ctx.beginPath();
     ctx.moveTo(cOriginX, yoffset); // y-axis top
     ctx.lineTo(cOriginX, cOriginY);
     ctx.lineTo(cWidth - nxoffset, cOriginY); // x-axis end
     ctx.stroke();
     ctx.closePath();
     
     // y-axis arrow head
     ctx.beginPath();
     ctx.moveTo(cOriginX, yoffset); // top of the y-axis
     ctx.lineTo(cOriginX-5,yoffset);
     ctx.lineTo(cOriginX,yoffset-5);
     ctx.lineTo(cOriginX+5,yoffset);
     ctx.lineTo(cOriginX,yoffset);
     ctx.fill();
     ctx.closePath();
     
     // x-axis arrow head
     ctx.beginPath()
     strtx = cWidth - nxoffset;
     ctx.moveTo(strtx, cOriginY); // end of the x-axis .
     ctx.lineTo(strtx, cOriginY-5); // |
     ctx.lineTo(strtx+5, cOriginY); // |-
     ctx.lineTo(strtx, cOriginY+5); // |>
     ctx.lineTo(strtx, cOriginY);
     ctx.fill();
     ctx.closePath();

     // axis labels
//     ctx.fillText("Time",(eWidth/2)+xoffset,(cHeight-nyoffset+10));
//     ctx.fillText("Speed", 1,(eHeight/2)+yoffset);
}

function getScaleFactor() {
     // scale highest value to be at highest point
     allData = UpData.concat(DownData);
     allMax = Math.max.apply(Math, allData);
     
     scaleF = allMax / eHeight;
     return scaleF;
}
function getLoadSF() {
    max = Math.max.apply(Math, LoadData);
    scaleF = max / eHeight;
    return scaleF
}

function getMemSF() {
    max = Math.max.apply(Math, MemData);
    scaleF = max / eHeight;
    return scaleF
}

function update_canvas() {
     netctx.clearRect(0, 0, cWidth - nxoffset, cHeight);
     sysctx.clearRect(0, 0, cWidth - nxoffset, cHeight);
     drawAxes(netctx);
     drawAxes(sysctx);
     scale_factor = getScaleFactor();

     // load average data
     loadSF = getLoadSF();
     sysctx.beginPath();
     sysctx.strokeStyle = "rgb(255,0,0)";
     startY = eHeight - (LoadData[0] / loadSF) + yoffset + 1;
     sysctx.moveTo(cOriginX + 1, startY);
     for (i=0; i<DownData.length; i++) {
         ld_y = eHeight - (LoadData[i] / loadSF) + yoffset;
         sysctx.lineTo(cOriginX + i*2 + 1, ld_y);
     }
     sysctx.stroke();
     sysctx.closePath();
   
     // mem data
     /*
     * memSF = getMemSF();
     * sysctx.beginPath();
     * sysctx.strokeStyle = "rgb(0,0,255)";
     * startY = eHeight - (MemData[0] / memSF) + yoffset + 1;
     * sysctx.moveTo(cOriginX + 1, startY);
     * for (i=0; i<MemData.length; i++) {
     *    mm_y = eHeight - (MemData[i] / memSF) + yoffset;
     *    sysctx.lineTo(cOriginX + i*2 + 1, mm_y);
     * }
     * sysctx.stroke();
     * sysctx.closePath();
     */

     // uprate data
     netctx.beginPath();
     netctx.strokeStyle = "rgb(255,0,0)";
     startY = eHeight - (UpData[0] / scale_factor) + yoffset + 1;
     netctx.moveTo(cOriginX + 1, startY);
     for (i=0;i<UpData.length;i++) {
          up_y = eHeight - (UpData[i] / scale_factor) + yoffset;
          netctx.lineTo(cOriginX + i*2 + 1, up_y);
          // x position = i*2
          // y position = re-scaled
          
          //netctx.moveTo(i*2,)
     }
     netctx.stroke();
     netctx.closePath();
     
     // downrate data
     netctx.beginPath();
     netctx.strokeStyle = "rgb(0,0,255)";
     startY = eHeight - (DownData[0] / scale_factor) + yoffset + 1;
     netctx.moveTo(cOriginX + 1, startY);
     for (i=0; i<DownData.length; i++) {
          dn_y = eHeight - (DownData[i] / scale_factor) + yoffset;
          netctx.lineTo(cOriginX + i*2 + 1, dn_y);
     }
     netctx.stroke();
     netctx.closePath();
}

function clearCanvas() {
     $(netctx).attr("width", $(netctx).attr("width"));
}

function init() {
     mainLoop();
}

function onMessage(e) {
     if (e.data.indexOf("ERROR") !== -1) {
          $("#status-div").removeClass("status-ok status-bad").addClass("status-bad").html(
               "StatSocket ERROR: " + e.data.split("ERROR/")[1]
          );
          return false;
     } else {
          data = JSON.parse(e.data);
          $("#status-uprate").html("<div class='status-label'>Upload rate:</div><div class='status-uprate-value status-value'>" + data.uprate_str + "/s</div>");
          $("#status-downrate").html("<div class='status-label'>Download rate:</div><div class='status-downrate-value status-value'>" + data.downrate_str + "/s</div>");
          $("#status-loadavg").html("<div class='status-label'>Load average:</div><div class='status-loadavg-value status-value'>" + data.loadavg + "</div>");
//          $("#status-mem").html("<div class='status-label'>Memory usage:</div><div class='status-mem-value status-value'>" + data.memusage + "%</div>");
          if (UpData.push(data.uprate) > maxValues) {
               UpData.shift();
          }
          if (DownData.push(data.downrate) > maxValues) {
               DownData.shift();
          }
          if (LoadData.push(data.loadavg) > maxValues) {
               LoadData.shift();
          }
          if (MemData.push(data.memusage) > maxValues) {
               MemData.shift();
          }

          if (UpData.length < 60) {
              $("#canvas-title-dynamic").html("(Last " + UpData.length + " seconds)");
          } else {
              mins = Math.floor(UpData.length/60);
              secs = UpData.length%60;
              if (mins == 1) {  
                  mins = "Last minute";
              } else {
                  mins = "Last " + mins + " minutes";
              }
              if (secs == 0) {
                  secs = "";
              } else {
                  secs = " and " + secs + " seconds";
              }
              $("#canvas-title-dynamic").html("(" + mins + secs + ")");
          }
          update_canvas();
     }
     return false;
}

function onOpen(e) {
    console.log("StatSocket opened", e, StatSocket);
    initGraph();
    init();
}

function onClose(e) {
    console.log("StatSocket closed", e, StatSocket);
}

function onError(e) {
    console.log("StatSocket Error", e, StatSocket);
}