var StatSocket = null;
var UpData = new Array();
var DownData = new Array();
var ctx = null;
var cHeight = null; // canvas total height (specified in HTML)
var cWidth = null; // canvas total width (specified in HTML)
var cOriginX = null; // bottom left of axes
var cOriginY = null; // bottom left of axes
var eHeight = null; // effective height (i.e. top of graph to bottom of axes)
var eWidth = null; // effective width (i.e. y-axis to left-most edge of graph)
var xoffset = 6; // distance between canvas left edge and y-axis
var yoffset = 6; // distance between canvas top edge and top of the y-axis
var nxoffset = 55; // distance between canvas right edge and end of x-axis
var nyoffset = 6; // distance between canvas bottom edge and x-axis
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
     StatSocket.send("request=globalspeed");
     setTimeout(mainLoop, 1000);
}

function initGraph() {
     cHeight = parseInt($("#canvas-actual").height());
     cWidth = parseInt($("#canvas-actual").width());
     
     cOriginX = xoffset;
     cOriginY = cHeight - nyoffset;
     eHeight = cOriginY - yoffset;
     eWidth = cWidth - xoffset - nxoffset;
     
     maxValues = Math.floor(eWidth / 2);
     
     clearCanvas($("#canvas-actual"));
     var canvas = document.getElementById("canvas-actual");
     ctx = canvas.getContext("2d");
     drawAxes();
     drawLegend();
}

function drawLegend() {
     
     ctx.fillStyle = "rgb(255,0,0)";
     ctx.beginPath();
     startX = cWidth - (nxoffset - 5);
     startY = (cHeight / 2) - 20;
     ctx.moveTo(startX, startY);
     ctx.lineTo(startX + (nxoffset-5), startY);
     ctx.lineTo(startX + (nxoffset-5), startY+10);
     ctx.lineTo(startX, startY+10);
     ctx.lineTo(startX, startY);
     ctx.fill();
     ctx.closePath();
     ctx.fillText("Upload", startX, startY + 20);
     
     ctx.fillStyle = "rgb(0,0,255)";
     ctx.beginPath();
     startX = cWidth - (nxoffset - 5);
     startY = (cHeight / 2) + 20;
     ctx.lineTo(startX + (nxoffset-5), startY);
     ctx.lineTo(startX + (nxoffset-5), startY+10);
     ctx.lineTo(startX, startY+10);
     ctx.lineTo(startX, startY);
     ctx.fill();
     ctx.closePath();
     ctx.fillText("Download", startX, startY + 20);
}

function drawAxes() {
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
}

function getScaleFactor() {
     // scale highest value to be at highest point
     allData = UpData.concat(DownData);
     allMax = Math.max.apply(Math, allData);
     
     scaleF = allMax / eHeight;
     return scaleF;
}

function update_canvas() {
     ctx.clearRect(0, 0, cWidth - nxoffset, cHeight - nyoffset);
     drawAxes();
     scale_factor = getScaleFactor();
     
     // uprate data
     ctx.beginPath();
     ctx.strokeStyle = "rgb(255,0,0)";
     startY = eHeight - (UpData[0] / scale_factor) + yoffset + 1;
     ctx.moveTo(cOriginX + 1, startY);
     for (i=0;i<UpData.length;i++) {
          up_y = eHeight - (UpData[i] / scale_factor) + yoffset;
          ctx.lineTo(cOriginX + i*2 + 1, up_y);
          // x position = i*2
          // y position = re-scaled
          
          //ctx.moveTo(i*2,)
     }
     ctx.stroke();
     ctx.closePath();
     
     // downrate data
     ctx.beginPath();
     ctx.strokeStyle = "rgb(0,0,255)";
     startY = eHeight - (DownData[0] / scale_factor) + yoffset + 1;
     ctx.moveTo(cOriginX + 1, startY);
     for (i=0; i<DownData.length; i++) {
          dn_y = startY = eHeight - (DownData[i] / scale_factor) + yoffset;
          ctx.lineTo(cOriginX + i*2 + 1, dn_y);
     }
     ctx.stroke();
     ctx.closePath();
}

function clearCanvas() {
     $(ctx).attr("width", $(ctx).attr("width"));
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
          $("#status-uprate").html("<div class='status-uprate-label'>Upload rate:</div><div class='status-uprate-value'>" + data.uprate_str + "/s</div>");
          $("#status-downrate").html("<div class='status-downrate-label'>Download rate:</div><div class='status-downrate-value'>" + data.downrate_str + "/s</div>");
          if (UpData.push(data.uprate) > maxValues) {
               UpData.shift();
          }
          if (DownData.push(data.downrate) > maxValues) {
               DownData.shift();
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