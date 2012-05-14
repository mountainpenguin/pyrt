var StatSocket = null;
var UpData = new Array();
var DownData = new Array();
var LoadData = new Array();
var MemData = new Array();
var netctx = null;
var sysctx = null;
var iolayer = null;
var tiplayer = null;
var iostage = null;
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
var trackerData = null;
var pieSlices = new Object();

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

function initTGraph() {
    clearCanvas($("#canvas-io"));
//    var iocanvas = document.getElementById("canvas-io");
//    var ioctx = iocanvas.getContext("2d");
    iostage = new Kinetic.Stage({
        container : "canvas-io",
        width : 1000,
        height : 400
    });
    iolayer = new Kinetic.Layer();
    
    createPie(iolayer, 150, 150, "up_total", "upShare");
    createPie(iolayer, 400, 150, "down_total", "downShare");
    createPie(iolayer, 650, 160, "ratio", "ratioShare");
    iostage.add(iolayer);
//    drawTUp(ioctx);
//    drawTDown(ioctx);
//    drawTRatio(ioctx);
}

function createPie(layer, originX, originY, totalkey, sharekey) {
    var slices = new Array();
    var oX = originX;
    var oY = originY;
    var currX = oX + 100;
    var currY = oY;
    var currA = 0;
    var endA = 0;
    var radius = 100;
    var styles = [ "rgb(0,0,0)", "rgb(0,0,255)", "rgb(0,255,0)", "rgb(255,0,0)",
                   "rgb(0,255,255)", "rgb(255,0,255)", "rgb(255,255,0)", "rgb(150,0,0)",
                   "rgb(0,150,0)", "rgb(0,0,150)", "rgb(0,150,150)", "rgb(150,0,150)",
                   "rgb(150,150,0)", "rgb(150,150,150)" ]
    var styleidx = 0;
    for (var tracker in trackerData) {
        if (trackerData.hasOwnProperty(tracker)) {
            var instruct = new Object();
            instruct.strokeStyle = styles[styleidx];
            instruct.fillStyle = styles[styleidx];
            instruct.startA = currA;
            instruct.originX = oX;
            instruct.originY = oY;
            instruct.radius = radius;
            data = trackerData[tracker];
            instruct.tracker = tracker;
            instruct.favicon = data.favicon;
            instruct.tot = data[totalkey];
            upshare = data[sharekey];
            instruct.share = upshare
            endA = currA + (upshare * Math.PI * 2);
            instruct.endA = endA;
            instruct.startX = currX;
            instruct.startY = currY;
            halfPos = calcHalfPos(currA, oX, oY, radius);
            instruct.startHalfX = halfPos[0];
            instruct.startHalfY = halfPos[1];
            endhalfPos = calcHalfPos(endA, oX, oY, radius);
            instruct.endHalfX = endhalfPos[0];
            instruct.endHalfY = endhalfPos[1];
            endPos = calcHalfPos(endA, oX, oY, radius, 1.0);
            currX = endPos[0];
            currY = endPos[1];
            instruct.endX = endPos[0];
            instruct.endY = endPos[1];
            currA = endA;

            obj = drawShape(instruct);
            pieSlices[obj.attrs.fill + "." + oX] = instruct;
            obj.on("mouseover", function(evt) {
                if (evt.x >= 50 && evt.x <= 250) {
                    var append = ".150";
                } else if (evt.x >= 300 && evt.x <= 500) {
                    var append = ".400";
                } else if (evt.x >= 550 && evt.x <= 750) {
                    var append = ".650";
                }
                var d = pieSlices[this.attrs.fill+append];
                this.setStroke("black");
                this.attrs.strokeWidth = 3;
                iolayer.draw();
            });
            obj.on("mouseout", function(evt) {
                this.setStroke(this.attrs.fill); 
                this.attrs.strokeWidth = 1;
                iolayer.draw();
            });
            obj.on("click", function(evt) {
                if (evt.x >= 50 && evt.x <= 250) {
                    var append = ".150";
                } else if (evt.x >= 300 && evt.x <= 500) {
                    var append = ".400";
                } else if (evt.x >= 550 && evt.x <= 750) {
                    var append = ".650";
                }
                pieToolTip(this, pieSlices[this.attrs.fill + append]); 
            });
            slices.push(obj);
            styleidx++;
            layer.add(obj);
        }
    }
}

function nearestBoundary(x) {
    var b = [ 25, 275, 525, 775 ]
    var diffs = new Array();
    for (i=0; i<b.length; i++) {
        diffs.push(Math.abs(x-b[i]));
    }
    mindiff = Math.min.apply(Math, diffs);
    idx = diffs.indexOf(mindiff);
    return b[idx];
}

function pieToolTip(shape, instruct) {
    console.log("shape", shape, "instruct", instruct);
    theta1 = instruct.startA;
    theta2 = instruct.endA;
    angle = theta1 + (theta2 - theta1) / 2
    startPos = calcHalfPos(angle, instruct.originX, instruct.originY, instruct.radius, 1.0);
    endPos = calcHalfPos(angle, instruct.originX, instruct.originY, instruct.radius, 1.1);
    xboundary = nearestBoundary(endPos[0]);
    var line = new Kinetic.Line({
        points : [startPos[0], startPos[1], endPos[0], endPos[1], xboundary, endPos[1]],
        stroke : instruct.strokeStyle,
        strokeWidth : 4,
        lineCap : "round"
    });
    console.log(iostage);
    if (tiplayer !== null) {
        iostage.remove(tiplayer);
    }
    tiplayer = new Kinetic.Layer();
    tiplayer.add(line);
    iostage.add(tiplayer);
    tiplayer.draw();
}

function drawShape(instruct) {
    var shape = new Kinetic.Shape({
        drawFunc: function() {
            var ctx = this.getContext("2d");
            ctx.beginPath();
            ctx.moveTo(instruct.startHalfX, instruct.startHalfY);
            ctx.lineTo(instruct.startX, instruct.startY);
            ctx.arc(instruct.originX, instruct.originY, instruct.radius, instruct.startA, instruct.endA, false);
            ctx.moveTo(instruct.endX, instruct.endY);
            ctx.lineTo(instruct.endHalfX, instruct.endHalfY);
            ctx.arc(instruct.originX, instruct.originY, instruct.radius/2, instruct.endA, instruct.startA, true);
            ctx.fill();
            this.applyStyles();
        },
        fill: instruct.fillStyle,
        stroke: instruct.strokeStyle,
        strokeWidth: 1
    });
    return shape;
}

function calcHalfPos(angle, centreX, centreY, radius, factor) {
    if ( factor == undefined) {
        factor = 0.5;
    }
    halfPosX = null;
    halfPosY = null;
    if (angle <= Math.PI/2) {
        halfPosX = centreX + (radius * factor) * Math.cos(angle);
        halfPosY = centreY + (radius * factor) * Math.sin(angle);
    } else if (angle > Math.PI/2 && angle <= Math.PI) {
        halfPosX = centreX - (radius * factor) * Math.sin(angle - Math.PI/2);
        halfPosY = centreY + (radius * factor) * Math.cos(angle - Math.PI/2);
    } else if (angle > Math.PI && angle <= 3*Math.PI/2) {
        halfPosX = centreX - (radius * factor) * Math.cos(angle - Math.PI);
        halfPosY = centreY - (radius * factor) * Math.sin(angle - Math.PI);
    } else if (angle > 3*Math.PI/2) {
        halfPosX = centreX + (radius * factor) * Math.sin(angle - 3*Math.PI/2);
        halfPosY = centreY - (radius * factor) * Math.cos(angle - 3*Math.PI/2);
    }
    return new Array(halfPosX, halfPosY);
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
     StatSocket.send("request=trackers");
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
          if (data.type == "trackers") {
              trackerData = data.data;
              initTGraph();
          } else if (data.type == "global") {
              $("#status-uprate").html("<div class='status-label'>Upload rate:</div><div class='status-uprate-value status-value'>" + data.uprate_str + "/s</div>");
              $("#status-downrate").html("<div class='status-label'>Download rate:</div><div class='status-downrate-value status-value'>" + data.downrate_str + "/s</div>");
              $("#status-loadavg").html("<div class='status-label'>Load average:</div><div class='status-loadavg-value status-value'>" + data.loadavg + "</div>");
//              $("#status-mem").html("<div class='status-label'>Memory usage:</div><div class='status-mem-value status-value'>" + data.memusage + "%</div>");
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
