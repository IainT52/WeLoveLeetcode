/*

Init

*/
// Init Canvas State
var canvas = $("#drawing-board"), colorSelector = $("#ctx-color")
var ctx = canvas[0].getContext('2d')
var offset = canvas.offset()
var curPos = { x: 0, y: 0 }
var colors = {'blue':'#0066ff', 'green':'#009933', 'red':'#c0392b', 'yellow':'#c0392b', 'pink':'#ff33cc', 'purple':'#9933ff', 'orange':'#ff6600', 'brown':'#996633', 'black':'#000000'}

var clicking = false, drawColor = '#000000', mouseUp = true

// Establish a WebSocket connection with the server
const socket = new WebSocket('ws://' + window.location.host + '/websocket');


/*

WEBSOCKET

*/


// Call the updateCanvas function whenever data is received from the server over the WebSocket
socket.onmessage = updateCanvas;

// Send an x,y coordinate of the current point drawn
function sendCoordinate(pos) {
    socket.send(JSON.stringify(pos))
}

function sendMessage() {
    let recipient = document.getElementById('recipient');
    let message = document.getElementById('msg');
    let data = { 'recipient': recipient.value, 'message': message.value };
    message.value = "";  // clear message box to prevent spam
    socket.send(JSON.stringify(data))
}

function receivedDirectMessage(directMessage) {
    recipientName = directMessage['recipient'];
    senderName = directMessage['sender'];
    if (recipientName == senderName) {
        alert('ERROR: The recipient does not exist or you sent a message to yourself!');
        return
    }
    message = directMessage['message'];
    directMessagesDiv = document.getElementById('direct-messages');
    messageHistory = directMessagesDiv.innerHTML;
    newMessage = `[From '${senderName}']: ${message}<br/>`;
    directMessagesDiv.innerHTML = messageHistory + newMessage;
    return
}


// Called when the server sends a new coordinate over the WebSocket and draw it to the canvas
function updateCanvas(message) {
    let coordinate = JSON.parse(message.data)
    if (!(coordinate.hasOwnProperty('x') && coordinate.hasOwnProperty('y'))) {
        receivedDirectMessage(coordinate);
        return
    }
    if (coordinate.x === -1 && coordinate.y == -1) {
        mouseUp = true
        return
    }
    if (mouseUp) {
        setNewUpdatePos(coordinate.x, coordinate.y)
        mouseUp = false
        return
    }
    ctx.beginPath()

    ctx.lineWidth = 1
    ctx.lineCap = 'round'
    ctx.strokeStyle = coordinate.color

    ctx.moveTo(curPos.x, curPos.y)
    setNewUpdatePos(coordinate.x, coordinate.y)
    ctx.lineTo(curPos.x, curPos.y)

    ctx.stroke()
}

function setNewUpdatePos(x, y) {
    curPos.x = x
    curPos.y = y
    return
}


/*

 CANVAS

*/
resize()


// Event listeners
canvas.mousedown(e => { setPosition(e), clicking = true })
canvas.mousemove(draw)
canvas.mouseup(e => { sendCoordinate({ x: -1, y: -1 }), clicking = false })
canvas.mouseout(e => clicking = false)
$("#ctx-color").change(e => drawColor = e.target.value)
$(window).resize(resize)


function setPosition(x, y) {
    curPos.x = x - offset.left
    curPos.y = y - offset.top
    return
}


function draw(e) {
    if (clicking) {
        ctx.beginPath()

        ctx.lineWidth = 1
        ctx.lineCap = 'round'
        ctx.strokeStyle = drawColor

        ctx.moveTo(curPos.x, curPos.y)
        setPosition(e.clientX, e.clientY)
        ctx.lineTo(curPos.x, curPos.y)

        ctx.stroke()
        sendCoordinate({...curPos, color:drawColor})
    }
}


function resize() {
    ctx.canvas.width = canvas.width()
    ctx.canvas.height = canvas.height()
    offset = canvas.offset()
}