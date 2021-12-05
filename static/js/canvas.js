/*

WEBSOCKET

*/

// Establish a WebSocket connection with the server
const socket = new WebSocket('ws://' + window.location.host + '/websocket');

// Call the updateCanvas function whenever data is received from the server over the WebSocket
socket.onmessage = updateCanvas;

// Send an x,y coordinate of the current point drawn
function sendCoordinate(pos) {
    socket.send(JSON.stringify(pos))
}

var mouseUp = false
// Called when the server sends a new coordinate over the WebSocket and draw it to the canvas
function updateCanvas(message) {
    let coordinate = JSON.parse(message.data)
    if (coordinate.x === -1 && coordinate.y == -1){
        mouseUp = true
        return
    }
    if (mouseUp){
        setPosition(coordinate.x, coordinate.y)
        mouseUp = false
        return
    }
    ctx.beginPath()

    ctx.lineWidth = 1
    ctx.lineCap = 'round'
    ctx.strokeStyle = '#c0392b'

    ctx.moveTo(curPos.x, curPos.y)
    setPosition(coordinate.x, coordinate.y)
    ctx.lineTo(curPos.x, curPos.y)
    
    ctx.stroke()
}


// Socket close event
socket.onclose = function (event) {
    if (event.wasClean) {
        console.log(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`)
    } else {
        alert('[close] Connection died')
    }
};


/*

 CANVAS

*/


// Init Canvas State
var canvas = $("#drawing-board")
var ctx = canvas[0].getContext('2d')
var offset = canvas.offset()
var curPos = {x: 0, y: 0}
var clicking = false
resize()


// Event listeners
canvas.mousedown(e => {setPosition(e), clicking = true})
canvas.mousemove(draw)
canvas.mouseup(e => {sendCoordinate({x:-1, y:-1}), clicking = false})
canvas.mouseout(e => clicking = false)
$( window ).resize(resize)


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
        ctx.strokeStyle = '#c0392b'

        ctx.moveTo(curPos.x, curPos.y)
        setPosition(e.clientX, e.clientY)
        ctx.lineTo(curPos.x, curPos.y)
        
        ctx.stroke()
        sendCoordinate(curPos)
    }
}


function resize() {
    ctx.canvas.width = canvas.width()
    ctx.canvas.height = canvas.height()
    offset = canvas.offset()
}