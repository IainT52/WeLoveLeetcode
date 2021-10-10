// Init Canvas State
var canvas = $("#drawing-board")
var ctx = canvas[0].getContext('2d')
var offset = canvas.offset()
var curPos = {x: 0, y: 0}
var clicking = false;
resize()


// Event listeners
canvas.mousedown(e => {setPosition(e), clicking = true})
canvas.mousemove(draw)
canvas.mouseup(e => clicking = false)
canvas.mouseout(e => clicking = false)
$( window ).resize(resize)


function setPosition(e) {
    curPos.x = e.clientX - offset.left
    curPos.y = e.clientY - offset.top
    return
}


function draw(e) {
    if (clicking) {
        ctx.beginPath();
        ctx.lineWidth = 1;
        ctx.lineCap = 'round';
        ctx.strokeStyle = '#c0392b';

        ctx.moveTo(curPos.x, curPos.y);
        setPosition(e);
        ctx.lineTo(curPos.x, curPos.y);

        ctx.stroke();
    }
}


function resize() {
    ctx.canvas.width = canvas.width()
    ctx.canvas.height = canvas.height()
    offset = canvas.offset()
}