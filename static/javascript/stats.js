var StatSocket = null;
var Data = new Array();

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
     StatSocket.send("request=globalspeed")
}

function initGraph() {
     var height = parseInt($("#canvas-actual").height());
     var width = parseInt($("#canvas-actual").width());
     clearCanvas($("#canvas-actual"));
     var canvas = document.getElementById("canvas-actual");
     var ctx = canvas.getContext("2d");
     ctx.strokeStyle = "rgb(0,0,0)";
     
     drawAxes(ctx, width, height);
     
}

function drawAxes(ctx, width, height) {
     var originX = 30
     var originY = height - 30;
     ctx.beginPath();
     ctx.moveTo(originX, 10);
     ctx.lineTo(originX, originY);
     ctx.lineTo(width - 30, originY);
     ctx.stroke();
     ctx.closePath();
}

function clearCanvas(ctx) {
     $(ctx).attr("width", $(ctx).attr("width"));
}

function init() {
     StatSocket.send("request=globalspeed");
}

function onMessage(e) {
    console.log("StatSocket message", e, StatSocket);
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