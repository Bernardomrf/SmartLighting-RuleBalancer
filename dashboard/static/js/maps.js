var states = {}
var values = {}

function setCanvasSize(){
	$('.plant-canvas').each(function() {
		var img = $(this).parent().find('.plant-image');
		var width = img.width();
		var height = img.height();
		var ctx = this.getContext("2d");
		ctx.canvas.width = width;
		ctx.canvas.height = height;
	});
}

function resizeImg(image){
	var maxWidth = $(document).width()/2;
	var maxHeight = $(document).height()/2;
	var ratio = 0;
	var width = image.width();
	var height = image.height();

	if(width > maxWidth){
		ratio = maxWidth / width;
		image.css("width", maxWidth);
		image.css("height", height * ratio);
		height = height * ratio;
		width = width * ratio;
	}

	if(height > maxHeight){
		ratio = maxHeight / height;
		image.css("height", maxHeight);
		image.css("width", width * ratio);
		width = width * ratio;
		height = height * ratio;
	}
}

function adjustModal(modal){
	resizeImg(modal.find('.plant-image'));
	var height = modal.find('.plant-image').height();
	modal.find('.plant-container').height(height);
}

$('.modal').on('shown.bs.modal', function (event) {
	adjustModal($(this));
	$('map').imageMapResize();
	setCanvasSize();
	setLastStates();
	setLastValues();
});

$('.modal').each( function() {
	$(this).find('area').each( function() {
		$(this).attr('title', $(this).attr('id'));
	});
});

function setLastState(device, state){
	switch(state.color){
		case 'blue':
			turnOnBlue(device, false);
			break;
		case 'green':
			turnOnGreen(device, false);
			break;
		case 'red':
			turnOnRed(device, false);
			break;
		case 'yellow':
			turnOnYellow(device, false);
			break;
		case 'none':
			turnOff(device, false);
			break;
		default:
			changeToColor(device, state.color);
	}
}

function setLastStates(){
	for (var device in states) {
		setLastState(device, states[device]);
	}
}

function setLastValues(){
	for (var device in values) {
		writeText(device, values[device]);
	}
}

function getWriteColor(red,green,blue){
	if ( (red*0.299 + green*0.8 + blue*0.114) > 186 )
		return '#000000';
	else {
		return '#ffffff';
	}
}

function changeToColor(device, color){
	$('[id='+device+']').each(function() {
		var position = $(this).attr('coords').split(',');
		var x = +position[0];
		var y = +position[1];
		var width = +position[2] -position[0];
		var height = +position[3] -position[1];
		var c = $(this).closest('div').find('.plant-canvas').get(0);
		var ctx = c.getContext("2d");
		ctx.fillStyle=color;
		ctx.fillRect(x,y,width,height);
	});
}

function writeText(device, text){
	$('[id='+device+']').each(function() {
		var position = $(this).attr('coords').split(',');
		var x = +position[0];
		var y = +position[1];
		var width = +position[2] -position[0];
		var height = +position[3] -position[1];
		var c = $(this).closest('div').find('.plant-canvas').get(0);
		var ctx = c.getContext("2d");

		var p = ctx.getImageData(x+1, y+1, 1, 1).data;
		ctx.fillStyle=getWriteColor(p[0], p[1], p[2]);
		ctx.font = "30px Arial";

		if (width > 30){
			var border = width/5;
			var fontsize = 50;
			do {
				fontsize--;
				ctx.font=fontsize+"px Arial";
			} while(ctx.measureText(text).width > (width - 2*border));
			ctx.fillText(text,x+border,y+(height/2)+(ctx.measureText('ii').width/2));
		}
		values[device] = text;
	});
}

function updateText(device, text){
	if (device in states){
		setLastState(device, states[device]);
	}
	writeText(device, text);
}

function turnOff(device, setLastText=true){
	changeToColor(device, '#ffffff');
	states[device] = {
		'color' : 'none'
	}
	if (setLastText && device in values){
		writeText(device, values[device]);
	}
}

function turnOnBlue(device, setLastText=true){
	changeToColor(device, '#0000ff');
	states[device] = {
		'color' : 'blue'
	}
	if (setLastText && device in values){
		writeText(device, values[device]);
	}
}

function turnOnGreen(device, setLastText=true){
	changeToColor(device, '#00ff00');
	states[device] = {
		'color' : 'green'
	}
	if (setLastText && device in values){
		writeText(device, values[device]);
	}
}

function turnOnRed(device, setLastText=true){
	changeToColor(device, '#ff0000');
	states[device] = {
		'color' : 'red'
	}
	if (setLastText && device in values){
		writeText(device, values[device]);
	}
}

function turnOnYellow(device, setLastText=true){
	changeToColor(device, '#fafd05');
	states[device] = {
		'color' : 'yellow'
	}
	if (setLastText && device in values){
		writeText(device, values[device]);
	}
}

$( document ).ready(function() {
	$('map').imageMapResize();
	$('[data-toggle="tooltip"]').tooltip();
	setCanvasSize();
});

window.onresize = function(event) {
	setCanvasSize();
	setTimeout(setLastStates, 500);
	setTimeout(setLastValues, 500);
	$('.modal').each(function() {
		adjustModal($(this));
	});
};