function Game(config) {
	this.config = config;
	this.canvas_width = 600;
	this.canvas_height = 400;
	this.font_loaded = false;
	this.dict_colors = {
		1: 'rgb(0,220,0)',
		2: 'magenta',
		3: 'black',
	}

	this.objects_word = null;
	this.objects_chars = null;
	this.selection_char_idx = null;
	this.list_alphabet = null;
	this.list_guessed = null;

	this.init();
}

Game.prototype.init = function () {
	this.load_font();
	this.canvas = document.getElementById(this.config.canvas_id);
	this.ctx = this.canvas.getContext("2d");
	this.canvas.width = this.canvas_width;
	this.canvas.height = this.canvas_height;
	this.init_objects();
	this.bind_events();
	this.render();
}

Game.prototype.load_font = function () {
	var font = new FontFace('Handwriting', 'url('+this.config.font_path+')');
	font.load().then(function(font){
		document.fonts.add(font);
		this.font_loaded = true;
		this.render()
	}.bind(this));	
}

Game.prototype.set_state = function(state) {
	this.state = state;
	console.log(state);
	this.calc_objects_rect();
	this.render();
}

Game.prototype.init_objects = function () {
	this.list_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split('');
	this.list_guessed = [];
	for(var i=0; i<this.list_alphabet.length; i++){
		this.list_guessed.push(false);
	}
}

Game.prototype.calc_objects_rect = function () {

	var dx = 30;
	var dy = 60;
	var x_start = 200;
	var x_end = this.canvas_width-40;

	var w = x_end - x_start
	var x = x_start+(w-this.state.word_to_guess.length*dx)/2;
	var y = 200;

	this.objects_won = {
		'x': x + w / 2,
		'y': y,
	}

	this.objects_word = [];
	for(var i=0; i<this.state.word_to_guess.length; i++){
		var c = this.state.word_to_guess[i].toUpperCase();
		this.objects_word.push({
			'x': x,
			'y': y,
			'c': c,
			'guessed': this.state.guesses.includes(c),
		})
		x += dx;
	}

	var dict_char_available = {};
	for(var i=0; i<this.state.list_action.length; i++){
		var action = this.state.list_action[i];
		dict_char_available[action.letter] = true;
	}

	this.objects_chars = [];
	var x = x_start;
	var y = this.canvas_height-95;
  	
	for(var i=0; i<this.list_alphabet.length; i++){
		var c = this.list_alphabet[i];
		this.objects_chars.push({
			'x': x,
			'y': y,
			'c': c.toUpperCase(),
			'rect': [x-10, y-28, 20, 30],
		})
		x += dx;
		if(x>x_end){
			x = x_start;
			y += dy*0.6;
		}
	}

}

Game.prototype.bind_events = function() {
	this.canvas.onmousemove = this.on_mouse_move.bind(this);
	this.canvas.onmousedown = this.on_mouse_down.bind(this);
}

Game.prototype.on_mouse_move = function(e) {
	if(this.state == null) return;
	if(this.state.phase != 'running') return;

 	var xy = this.get_xy_from_cursor(e);
 	var do_render = false;
 	var selection_char_idx = null;
	for(var i=0; i<this.objects_chars.length; i++){
		var char = this.objects_chars[i];
 		if(this.is_point_in_rect(xy, char.rect) && !this.list_guessed[i]) {
 			selection_char_idx = i;
 		}
	}
	if(this.selection_char_idx!=selection_char_idx) {
	 	this.selection_char_idx = selection_char_idx;
	 	do_render = true;
	}

 	if(do_render) {
 		this.render();
 	}
}

Game.prototype.on_mouse_down = function(e) {
	if(this.state == null) return;
	if(this.state.phase != 'running') return;

 	var xy = this.get_xy_from_cursor(e);
	for(var i=0; i<this.objects_chars.length; i++){
		var char = this.objects_chars[i];
		if(this.list_guessed[i]) continue;
 		if(this.is_point_in_rect(xy, char.rect) && this.selection_char_idx == i) {
 			this.selection_char_idx = null;
 			this.list_guessed[i] = true;
 			var action = {'letter': char.c};
	     	this.send_action_callback(action);
 		}
	}

	this.render();
}

Game.prototype.send_action_callback = function(action) {
}

Game.prototype.get_xy_from_cursor = function(e) {
 	var x = e.offsetX || (e.pageX - this.canvas.offsetLeft);
 	var y = e.offsetY || (e.pageY - this.canvas.offsetTop);
 	return [x, y];
}

Game.prototype.is_point_in_rect = function(xy, rect) {
	return xy[0]>rect[0] && xy[0]<rect[0]+rect[2] && xy[1]>rect[1] && xy[1]<rect[1]+rect[3];
}


// render
Game.prototype.render = function () {

	if(!this.font_loaded) return;

	var errors = this.state==null ? 0 : this.state.incorrect_guesses.length;

	var ctx = this.ctx;
	ctx.fillStyle = 'white';
	ctx.fillRect(0,0,this.canvas_width,this.canvas_height);

	// title
	ctx.font = "55px Handwriting";
	ctx.textAlign = "left";
	ctx.fillStyle = "black";
	ctx.fillText('Hangman', 40, 50);
	
	var x = 40;
	var y = 340;
	var s = 20;
	var lw = 2.5;
	var steps = [
		[[x,y,x,y-s*13], [x-s,y,x+s,y], [x-1,y-s*12-1,x+s+1,y-s*13-1], [x,y-s*13,x+s*5,y-s*13]],
		[[x+s*4,y-s*10,s*0.66]],
		[[x+s*4,y-s*9.22,x+s*4,y-s*7]],
		[[x+s*4,y-s*9,x+s*2.5,y-s*7.5]],
		[[x+s*4,y-s*9,x+s*5.5,y-s*7.5]],
		[[x+s*4,y-s*7,x+s*3,y-s*4]],
		[[x+s*4,y-s*7,x+s*5,y-s*4]],
		[[x+s*4,y-s*13-2,x+s*4,y-s*10.66-2]],
	];
	ctx.lineWidth = lw;
	ctx.lineCap = 'round';
	for(var i=steps.length-1; i>=0; i--){
		var lines = steps[i];
		for(var j=0; j<lines.length; j++){
			var l = lines[j];
			ctx.beginPath();
			if(l.length==4) {
				ctx.moveTo(l[0],l[1]);
				ctx.lineTo(l[2],l[3]);
			} else {
				ctx.arc(l[0],l[1],l[2],0,Math.PI*2);        
			}
			ctx.strokeStyle = i>=errors ? '#ccc' : 'black';
			ctx.stroke();
		}
	}

	if(this.state==null) return;

	ctx.font = "50px Handwriting";
	ctx.textAlign = "center";

	for(var i=0; i<this.objects_word.length; i++){
		var char = this.objects_word[i];
		if(char.c!='_') {
			if(char.guessed) {
				ctx.fillStyle = "black";
			} else {
				ctx.fillStyle = "red";
			}
			ctx.fillText(char.c, char.x, char.y);
		} /*else if(this.state.solution!='') {
			var s = this.state.solution[i];
			ctx.fillStyle = "red";
			ctx.fillText(s, char.x, char.y);
		}*/
		ctx.fillStyle = "black";
		ctx.fillText('_', char.x, char.y+5);
	}

	if(this.state.phase=='finished') {
		ctx.font = "50px Handwriting";
		ctx.textAlign = "center";
		if(errors<8) {
			ctx.fillStyle = this.dict_colors[1];
			ctx.fillText('You Won!', 360, 120);			
		} else {
			ctx.fillStyle = 'red';
			ctx.fillText('You Lose!', 360, 120);			
		}
	};

	ctx.lineWidth = 2;
	ctx.fillStyle = "black";
	for(var i=0; i<this.objects_chars.length; i++){
		var char = this.objects_chars[i];
		ctx.fillText(char.c, char.x, char.y);

		if(this.list_guessed[i]) {
			ctx.strokeStyle = "black";
			ctx.beginPath();
			ctx.moveTo(char.x-10,char.y-3);
			ctx.lineTo(char.x+10,char.y-18);
			ctx.stroke();
			ctx.beginPath();
			ctx.moveTo(char.x+10,char.y-3);
			ctx.lineTo(char.x-10,char.y-18);
			ctx.stroke();		
		} else {
			if(i==this.selection_char_idx) {
				ctx.lineWidth = 2;
				ctx.strokeStyle = this.dict_colors[1];
				ctx.strokeRect(char.rect[0], char.rect[1], char.rect[2], char.rect[3]);
			}
		}

	}

}
