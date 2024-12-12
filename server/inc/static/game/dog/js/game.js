function Game(config) {
	this.config = config;
	this.canvas_width = 1440;
	this.canvas_height = 1550;
	this.list_assets = [
		{'id':'board_0', 'src':'boards/board_blue.png'},
		{'id':'board_1', 'src':'boards/board_green.png'},
		{'id':'board_2', 'src':'boards/board_red.png'},
		{'id':'board_3', 'src':'boards/board_yellow.png'},
		{'id':'ball_0', 'src':'balls/ball_blue.png'},
		{'id':'ball_1', 'src':'balls/ball_green.png'},
		{'id':'ball_2', 'src':'balls/ball_red.png'},
		{'id':'ball_3', 'src':'balls/ball_yellow.png'},
		{'id':'card_♣A', 'src':'cards/ace_of_clubs.png'},
		{'id':'card_♦A', 'src':'cards/ace_of_diamonds.png'},
		{'id':'card_♥A', 'src':'cards/ace_of_hearts.png'},
		{'id':'card_♠A', 'src':'cards/ace_of_spades.png'},
		{'id':'card_♣2', 'src':'cards/2_of_clubs.png'},
		{'id':'card_♦2', 'src':'cards/2_of_diamonds.png'},
		{'id':'card_♥2', 'src':'cards/2_of_hearts.png'},
		{'id':'card_♠2', 'src':'cards/2_of_spades.png'},
		{'id':'card_♣3', 'src':'cards/3_of_clubs.png'},
		{'id':'card_♦3', 'src':'cards/3_of_diamonds.png'},
		{'id':'card_♥3', 'src':'cards/3_of_hearts.png'},
		{'id':'card_♠3', 'src':'cards/3_of_spades.png'},
		{'id':'card_♣4', 'src':'cards/4_of_clubs.png'},
		{'id':'card_♦4', 'src':'cards/4_of_diamonds.png'},
		{'id':'card_♥4', 'src':'cards/4_of_hearts.png'},
		{'id':'card_♠4', 'src':'cards/4_of_spades.png'},
		{'id':'card_♣5', 'src':'cards/5_of_clubs.png'},
		{'id':'card_♦5', 'src':'cards/5_of_diamonds.png'},
		{'id':'card_♥5', 'src':'cards/5_of_hearts.png'},
		{'id':'card_♠5', 'src':'cards/5_of_spades.png'},
		{'id':'card_♣6', 'src':'cards/6_of_clubs.png'},
		{'id':'card_♦6', 'src':'cards/6_of_diamonds.png'},
		{'id':'card_♥6', 'src':'cards/6_of_hearts.png'},
		{'id':'card_♠6', 'src':'cards/6_of_spades.png'},
		{'id':'card_♣7', 'src':'cards/7_of_clubs.png'},
		{'id':'card_♦7', 'src':'cards/7_of_diamonds.png'},
		{'id':'card_♥7', 'src':'cards/7_of_hearts.png'},
		{'id':'card_♠7', 'src':'cards/7_of_spades.png'},
		{'id':'card_♣8', 'src':'cards/8_of_clubs.png'},
		{'id':'card_♦8', 'src':'cards/8_of_diamonds.png'},
		{'id':'card_♥8', 'src':'cards/8_of_hearts.png'},
		{'id':'card_♠8', 'src':'cards/8_of_spades.png'},
		{'id':'card_♣9', 'src':'cards/9_of_clubs.png'},
		{'id':'card_♦9', 'src':'cards/9_of_diamonds.png'},
		{'id':'card_♥9', 'src':'cards/9_of_hearts.png'},
		{'id':'card_♠9', 'src':'cards/9_of_spades.png'},
		{'id':'card_♣10', 'src':'cards/10_of_clubs.png'},
		{'id':'card_♦10', 'src':'cards/10_of_diamonds.png'},
		{'id':'card_♥10', 'src':'cards/10_of_hearts.png'},
		{'id':'card_♠10', 'src':'cards/10_of_spades.png'},
		{'id':'card_♣J', 'src':'cards/jack_of_clubs.png'},
		{'id':'card_♦J', 'src':'cards/jack_of_diamonds.png'},
		{'id':'card_♥J', 'src':'cards/jack_of_hearts.png'},
		{'id':'card_♠J', 'src':'cards/jack_of_spades.png'},
		{'id':'card_♣Q', 'src':'cards/queen_of_clubs.png'},
		{'id':'card_♦Q', 'src':'cards/queen_of_diamonds.png'},
		{'id':'card_♥Q', 'src':'cards/queen_of_hearts.png'},
		{'id':'card_♠Q', 'src':'cards/queen_of_spades.png'},
		{'id':'card_♣K', 'src':'cards/king_of_clubs.png'},
		{'id':'card_♦K', 'src':'cards/king_of_diamonds.png'},
		{'id':'card_♥K', 'src':'cards/king_of_hearts.png'},
		{'id':'card_♠K', 'src':'cards/king_of_spades.png'},
		{'id':'card_JKR', 'src':'cards/joker.png'},
		{'id':'card_BCK', 'src':'cards/back.png'},
	]

	this.dict_id_card_nr = {};
	for(var i=0; i<this.list_assets.length; i++) {
		var asset = this.list_assets[i];
		if(asset.id.indexOf('card_')==0) {
			var id_card = asset.id.substr('card_'.length);
			if(!this.dict_id_card_nr.hasOwnProperty(id_card)) {
				this.dict_id_card_nr[id_card] = Object.keys(this.dict_id_card_nr).length;
			}
		}
	}

	this.dict_colors = {
		1: 'rgb(0,220,0)',
		2: 'magenta',
		3: 'black',
	}
	this.dict_players_colors = [
		'blue',
		'green',
		'red',
		'rgb(255, 204, 0)',
	]
	this.ID_BUTTON_SUBMIT = 'submit';
	this.ID_AREA_CARDS = 'cards';
	this.ID_AREA_EXCHANGE_CARDS = 'exchange_cards';
	this.ID_AREA_BOARD = 'baord';
	this.CNT_PLAYERS = 4
	this.CNT_BALLS = 4
	this.CNT_POS = 96
	this.CNT_STEPS = 64
	this.list_xy_pos = null;
	this.dict_player_card_rect = null;
	this.dict_exchange_card_rect = null;
	this.dict_area_rect = null;
	this.list_card_selectable = null;
	this.list_ball_selectable_from = null;
	this.list_ball_selectable_to = null;
	this.dict_imgs = null;
	this.player_state = null;
	this.selection_state = null;
	this.imgs_loaded = false;
	this.idx_player_you = 0;

	this.init();
}

Game.prototype.get_id_from_card = function (card) {
	return card.suit+card.rank;
}
Game.prototype.are_cards_equal = function (card_a, card_b) {
	if(card_a==null || card_b==null) {
		return card_a==card_b;
	}
	return card_a.suit==card_b.suit && card_a.rank==card_b.rank;
}

Game.prototype.init = function () {
	this.canvas = document.getElementById(this.config.canvas_id);
	this.ctx = this.canvas.getContext("2d");
	this.canvas.width = this.canvas_width;
	this.canvas.height = this.canvas_height;
	this.calc_xy_pos();
	this.load_images();
	this.bind_events();
}

Game.prototype.calc_xy_pos = function () {
	this.board_width = 860;
	this.r_active = 0.024*this.board_width;
	this.board_x = 290;
	this.board_y = 290;
	this.board_center_x = this.board_x + 0.4975*this.board_width;
	this.board_center_y = this.board_y + 0.4975*this.board_width;
	this.list_xy_pos = [
		[484,1088],		// 0
		[519,1054],		// 1
		[553,1020],		// 2
		[588,985],		// 3
		[623,951],		// 4
		[669,965],		// 5
		[719,970],		// 6
		[767,965],		// 7
		[814,951],		// 8
		[849,985],		// 9
		[883,1020],		// 10
		[917,1054],		// 11
		[951,1091],		// 12
		[991,1062],		// 13
		[1027,1028],	// 14
		[1059,992],		// 15
		[1087,953],		// 16
		[1054,917],		// 17
		[1020,883],		// 18
		[985,849],		// 19
		[951,814],		// 20
		[965,767],		// 21
		[970,718],		// 22
		[964,669],		// 23
		[951,623],		// 24
		[986,588],		// 25
		[1020,553],		// 26
		[1054,518],		// 27
		[1091,485],		// 28
		[1063,445],		// 29
		[1030,408],		// 30
		[993,376],		// 31
		[953,347],		// 32
		[917,382],		// 33
		[883,416],		// 34
		[848,452],		// 35
		[814,485],		// 36
		[767,470],		// 37
		[718,466],		// 38
		[671,473],		// 39
		[625,487],		// 40
		[589,451],		// 41
		[554,416],		// 42
		[519,382],		// 43
		[485,345],		// 44
		[446,374],		// 45
		[408,407],		// 46
		[376,444],		// 47
		[347,483],		// 48
		[382,518],		// 49
		[416,553],		// 50
		[452,588],		// 51
		[486,623],		// 52
		[470,670],		// 53
		[466,719],		// 54
		[473,767],		// 55
		[486,814],		// 56
		[451,848],		// 57
		[416,883],		// 58
		[382,917],		// 59
		[345,952],		// 60
		[374,991],		// 61
		[408,1028],		// 62
		[444,1059],		// 63

		[570,1088],		// 64
		[620,1088],		// 65
		[669,1088],		// 66
		[718,1088],		// 67
		[476,1013],		// 68
		[470,965],		// 69
		[505,931],		// 70
		[539,896],		// 71

		[1087,866],		// 72
		[1087,817],		// 73
		[1087,768],		// 74
		[1087,718],		// 75
		[1013,960],		// 76
		[964,965],		// 77
		[930,931],		// 78
		[895,896],		// 79

		[866,347],		// 80
		[816,347],		// 81
		[767,347],		// 82
		[718,347],		// 83
		[961,422],		// 84
		[965,470],		// 85
		[931,505],		// 86
		[897,540],		// 87
		
		[347,570],		// 88
		[347,620],		// 89
		[347,669],		// 90
		[347,717],		// 91
		[423,475],		// 92
		[472,470],		// 93
		[506,505],		// 94
		[541,541]		// 95
	]
}

Game.prototype.load_images = function () {
	this.dict_imgs = {}
	this.imgs_loaded = false;
	this.cnt_images_loaded = 0;

	for(var i=0; i<this.list_assets.length; i++) {
		var asset = this.list_assets[i];
		var img = new Image();
		img.src = this.config.img_path + asset['src'];
		img.onload = function() {
	      	this.cnt_images_loaded++;
			if(this.cnt_images_loaded==this.list_assets.length) {
				this.imgs_loaded = true;
				this.render();
			}
	    }.bind(this);
		this.dict_imgs[asset['id']] = img;
	}
}

Game.prototype.bind_events = function() {
	this.canvas.onmousemove = this.on_mouse_move.bind(this);
	this.canvas.onmousedown = this.on_mouse_down.bind(this);
}

Game.prototype.set_player_state = function(player_state) {
	this.selection_state = {
		'idx_card_hover': null,
		'idx_card_selected': null,
		'pos_from_selected': null,
		'idx_pos_hover': null,
		'idx_exchange_card_hover': null,
		'idx_exchange_card_selected': null,
		'pos_to_selected': null,
		'exchange_card_visible': false,
		'submit_button_state': null,
	};
	this.list_card_selectable = [];
	this.list_ball_selectable_from = [];
	this.list_ball_selectable_to = [];
	this.player_state = player_state;
	
	this.calc_board_rotation();
	this.calc_objects_rect();
	this.calc_selectable();
	this.render();
}

Game.prototype.calc_board_rotation = function() {
	// rotate xy of pos, pos numbering remains the same
	this.list_xy_pos_rotated = [];
	for(var idx=0; idx<this.CNT_STEPS; idx++) {
		var idx_to = (idx + this.CNT_STEPS - this.player_state.idx_player_you*16) % this.CNT_STEPS;
		this.list_xy_pos_rotated[idx_to] = this.list_xy_pos[idx];
	}
	for(var idx=this.CNT_STEPS; idx<this.CNT_POS; idx++) {
		var idx_to = this.CNT_STEPS + (idx + 32 - this.player_state.idx_player_you*8) % 32;
		this.list_xy_pos_rotated[idx_to] = this.list_xy_pos[idx];
	}

	// rotate players in this.player_state.list_player so that you are at 0
	var list_player = [];
	for(var idx=0; idx<4; idx++) {
		var idx_to = (idx + this.player_state.idx_player_you) % 4;
		list_player[idx_to] = this.player_state.list_player[idx];
		list_player[idx_to].idx_orig = idx;
	}
	this.player_state.list_player = list_player;
}


Game.prototype.calc_objects_rect = function() {
	this.dict_player_card_rect = {};

	var card_w = 0.3*500;
	var card_h = 0.3*726;
	var card_padding = 50;

	// cards center
	var card_x = this.board_center_x - 150;
	var card_y = this.board_center_y - 110;
	this.dict_player_card_rect.card_stack = [card_x+card_w+5, card_y, card_w, card_h];
	this.dict_player_card_rect.card_pile = [card_x, card_y, card_w, card_h];

	function sortCards(a,b) {
		var id_card_a = this.get_id_from_card(a);
		var id_card_b = this.get_id_from_card(b)
		return this.dict_id_card_nr[id_card_a] - this.dict_id_card_nr[id_card_b];
	}
	function sortEchangeCards(a,b) {
		return this.dict_id_card_nr[a.id_card] - this.dict_id_card_nr[b.id_card];
	}

	// sort players cards
	for(var p=0; p<4; p++) {
		var player = this.player_state.list_player[p];
		player.list_card.sort(sortCards.bind(this));
	}

	// cards players
	this.dict_player_card_rect.list_player = []
	for(var p=0; p<4; p++) {
		this.dict_player_card_rect.list_player[p] = [];
		if(p%2==0) {
			for(var i=0; i<this.player_state.list_player[p].list_card.length; i++) {
				card_x = this.board_center_x - (this.player_state.list_player[p].list_card.length*(card_w + 10) - 10)/2 + i*(card_w + 10);
				if(p==0) {
					card_y = this.board_y + this.board_width + card_padding;
				} else {
					card_y = this.board_y - card_padding - card_h;
				}
				this.dict_player_card_rect.list_player[p][i] = [card_x, card_y, card_w, card_h];
			}
		} else {
			for(var i=0; i<this.player_state.list_player[p].list_card.length; i++) {
				card_y = this.board_center_x + (this.player_state.list_player[p].list_card.length*(card_w + 10) - 10)/2 - i*(card_w + 10) - card_w;
				if(p==1) {
					card_x = this.board_y + this.board_width + card_padding;
				} else {
					card_x = this.board_y - card_padding - card_h;
				}
				this.dict_player_card_rect.list_player[p][i] = [card_x, card_y, card_h, card_w];
			}
		}
	}

	// exchange cards
	this.dict_exchange_card_rect = [];
	for(var i=0; i<this.player_state.list_action.length; i++) {
		var action = this.player_state.list_action[i];
		if(action.card_swap!=null) {
			
			// limit swap actions to ♥ cards, because of limited space!
			if(action.card.rank=='JKR' && action.card_swap.suit!='♥') continue;
     		
     		this.dict_exchange_card_rect.push({
     			'card': action.card_swap,
     		});
		}
	}
	// sort exchange cards
	this.dict_exchange_card_rect.sort(sortEchangeCards.bind(this));
	// calc rect
	for(var i=0; i<this.dict_exchange_card_rect.length; i++) {
		var exchange_card = this.dict_exchange_card_rect[i];
		card_x = this.board_center_x - (this.dict_exchange_card_rect.length*(card_w/2 + 10) - 10)/2 + i*(card_w/2 + 10);
		card_y = this.board_y + this.board_width + card_h + card_padding + 10;
		exchange_card.rect = [card_x, card_y, card_w/2, card_h/2];
	}

	this.dict_area_rect = {};

	// submit button
	var txt = 'Submit';
	var f = 24;
	var dx = 20;
	var dy = 20;
	this.ctx.font = f+'px Arial';
	var w = this.ctx.measureText(txt).width;
	this.dict_area_rect[this.ID_BUTTON_SUBMIT] = {
		'rect': [
			this.board_center_x-w/2-dx,
			this.board_center_y+this.board_width*0.85,
			w+dx*2,
			f+dy*2
		],
		'f': f,
		'txt': txt,
		'dx': dx,
		'dy': dy,
	}

	// area cards
	var w = (card_w+10)*6;
	this.dict_area_rect[this.ID_AREA_CARDS] = {
		'rect': [
			this.board_center_x-w/2,
			this.board_y + this.board_width + card_padding - 5,
			w,
			card_h + 10
		],
	}

	// area cards
	var x = 0;
	var y = 0;
	var w = 0;
	var h = 0;
	if(this.dict_exchange_card_rect.length>0) {
		x = this.dict_exchange_card_rect[0].rect[0]-5;
		y = this.dict_exchange_card_rect[0].rect[1];
		w = (this.dict_exchange_card_rect[0].rect[2]+10)*this.dict_exchange_card_rect.length;
		h = this.dict_exchange_card_rect[0].rect[3];
	}
	this.dict_area_rect[this.ID_AREA_EXCHANGE_CARDS] = {
		'rect': [
			x,
			y,
			w,
			h
		],
	}

	// area board
	this.dict_area_rect[this.ID_AREA_BOARD] = {
		'rect': [
			this.board_x,
			this.board_y,
			this.board_width,
			this.board_width
		],
	}

}

Game.prototype.calc_selectable = function() {
 	if(this.config.spectator || this.player_state.idx_player_active!=this.player_state.idx_player_you) {
 		return;
 	}

 	var player = this.player_state.list_player[this.idx_player_you];

	this.list_card_selectable = [];
	for(var j=0; j<player.list_card.length; j++) {
		this.list_card_selectable[j] = false;
	}

	this.list_ball_selectable_from = [];
	this.list_ball_selectable_to = [];
	for(var j=0; j<this.CNT_POS; j++) {
		this.list_ball_selectable_from[j] = false;
		this.list_ball_selectable_to[j] = false;
	}

 	// cards
 	var cnt_cards_selectable = 0;
 	var idx_cards_selectable = null;
	for(var i=0; i<this.player_state.list_action.length; i++) {
		var action = this.player_state.list_action[i];
     	for(var j=0; j<player.list_card.length; j++) {
     		var card = player.list_card[j];
     		if(this.are_cards_equal(action.card, card)) {
				this.list_card_selectable[j] = true;
				cnt_cards_selectable += 1;
				idx_cards_selectable = j;
     		}
     	}
	}
	if(cnt_cards_selectable==1) {
		this.selection_state.idx_card_selected = idx_cards_selectable;
	}


	if(this.player_state.bool_card_exchanged && this.selection_state.idx_card_selected!=null) {

     	// exchange cards
     	var cnt_exchange_cards_selectable = 0;
     	var idx_exchange_cards_selectable = null;
		var card = this.player_state.list_player[this.idx_player_you].list_card[this.selection_state.idx_card_selected];
		if(card.rank=='JKR') {
			for(var i=0; i<this.dict_exchange_card_rect.length; i++) {
				idx_exchange_cards_selectable = i;
	     		cnt_exchange_cards_selectable += 1
			}
		}

     	var cnt_balls_selectable = 0;
     	var idx_balls_selectable = null;
		for(var i=0; i<this.player_state.list_action.length; i++) {
			var action = this.player_state.list_action[i];
			var card = this.player_state.list_player[this.idx_player_you].list_card[this.selection_state.idx_card_selected];
     		if(this.are_cards_equal(action.card, card)) {
				this.list_ball_selectable_from[action.pos_from] = true;
				if(idx_balls_selectable!=action.pos_from) {
					cnt_balls_selectable += 1;
					idx_balls_selectable = action.pos_from;
				}
     		}
		}

		if(cnt_exchange_cards_selectable+cnt_balls_selectable==1) {
			if(cnt_exchange_cards_selectable==1) {
				this.selection_state.submit_button_state = 1;
			} else {
				this.selection_state.pos_from_selected = idx_balls_selectable;
			}
		}	     		

		this.selection_state.exchange_card_visible = cnt_exchange_cards_selectable>0 && this.selection_state.pos_from_selected==null;

     	if(this.selection_state.pos_from_selected!=null) {
	     	var cnt_balls_selectable = 0;
	     	var idx_balls_selectable = null;
			for(var i=0; i<this.player_state.list_action.length; i++) {
				var action = this.player_state.list_action[i];
				var card = this.player_state.list_player[this.idx_player_you].list_card[this.selection_state.idx_card_selected];
	     		if(this.are_cards_equal(action.card, card) && action.pos_from==this.selection_state.pos_from_selected) {
					this.list_ball_selectable_to[action.pos_to] = true;
					cnt_balls_selectable += 1;
					idx_balls_selectable = action.pos_to;
	     		}
			}
			if(cnt_balls_selectable==1) {
				this.selection_state.pos_to_selected = idx_balls_selectable;
				this.selection_state.submit_button_state = 1;
			}	     		
     	}		

	}

}


Game.prototype.on_mouse_move = function(e) {
 	if(this.can_select()) return;

 	var xy = this.get_xy_from_cursor(e);
 	var do_render = false;

 	// check submit button
 	if(this.selection_state.submit_button_state!=null) {
     	var submit_button_state_before = this.selection_state.submit_button_state;
     	this.selection_state.submit_button_state = this.get_id_button_from_xy(xy) == this.ID_BUTTON_SUBMIT ? 2 : 1;
     	do_render |= submit_button_state_before!=this.selection_state.submit_button_state;
 	}

 	// check cards
 	if(this.is_point_in_rect(xy, this.dict_area_rect[this.ID_AREA_CARDS].rect)) {
     	var idx_card_before = this.selection_state.idx_card_hover;
     	this.selection_state.idx_card_hover = this.get_idx_card_from_xy(xy);
     	do_render |= idx_card_before!=this.selection_state.idx_card_hover;
 	}

 	// check exchange cards
 	if(this.is_point_in_rect(xy, this.dict_area_rect[this.ID_AREA_EXCHANGE_CARDS].rect)) {
     	var idx_exchange_card_before = this.selection_state.idx_exchange_card_hover;
     	this.selection_state.idx_exchange_card_hover = this.get_idx_exchange_card_from_xy(xy);
     	do_render |= idx_exchange_card_before!=this.selection_state.idx_exchange_card_hover;
 	}

 	// chack balls
 	if(this.selection_state.idx_card_selected!=null) {
     	if(this.is_point_in_rect(xy, this.dict_area_rect[this.ID_AREA_BOARD].rect)) {
	     	var idx_pos_hover_before = this.selection_state.idx_pos_hover;
     		for(var i=0; i<this.CNT_POS; i++) {
     			if(this.list_ball_selectable_from[i] || this.list_ball_selectable_to[i]) {
     				this.selection_state.idx_pos_hover = this.get_idx_pos_from_xy(xy);
     			}
     		}
     		do_render |= idx_pos_hover_before!=this.selection_state.idx_pos_hover;
     	}
 	}

 	if(do_render) {
 		this.render();
 	}
}

Game.prototype.on_mouse_down = function(e) {
 	if(this.can_select()) return;

 	var xy = this.get_xy_from_cursor(e);

 	// check submit button
 	if(this.selection_state.submit_button_state!=null) {
     	if(this.is_point_in_rect(xy, this.dict_area_rect[this.ID_BUTTON_SUBMIT].rect)) {
	     	var id_button = this.get_id_button_from_xy(xy);
	     	if(id_button==this.ID_BUTTON_SUBMIT) {
	     		if(this.player_state.bool_card_exchanged) {
		     		var action = null;
		     		var idx_card = this.selection_state.idx_card_selected;
		     		var card = this.player_state.list_player[this.idx_player_you].list_card[idx_card];
		     		var pos_from = this.selection_state.pos_from_selected; 
		     		var pos_to = this.selection_state.pos_to_selected;
		     		var card_exchange = null;
		     		if(this.selection_state.idx_exchange_card_selected!=null){
		     			var exchange_card_rect = this.dict_exchange_card_rect[this.selection_state.idx_exchange_card_selected]
			     		card_exchange = exchange_card_rect.card;
		     		}
		     		//console.log(card, pos_from, pos_to, card_exchange)
		     		//console.log(this.player_state.list_action)
		     		for(var i=0; i < this.player_state.list_action.length; i++) {
		     			if((this.are_cards_equal(this.player_state.list_action[i].card, card)
		     					&& this.player_state.list_action[i].pos_from==pos_from
		     					&& this.player_state.list_action[i].pos_to==pos_to)
		     					|| (card_exchange!=null && this.are_cards_equal(this.player_state.list_action[i].card_swap, card_exchange))) {
		     				action = this.player_state.list_action[i];
		     				break;
		     			}
		     		}
		     		//console.log(action);
		     		this.send_action_callback(action);
		     		return;
	     		} else {
		     		var action = null;
		     		var idx_card = this.selection_state.idx_card_selected;
		     		var card = this.player_state.list_player[this.idx_player_you].list_card[idx_card];
		     		for(var i=0; i < this.player_state.list_action.length; i++) {
		     			if(this.are_cards_equal(this.player_state.list_action[i].card, card)) {
		     				action = this.player_state.list_action[i];
		     				break;
		     			}
		     		}
	     			this.send_action_callback(action);
	     			return; 			
	     		}
	     	}
	    }
	}

 	// check card selection
 	if(this.is_point_in_rect(xy, this.dict_area_rect[this.ID_AREA_CARDS].rect)) {
 		this.selection_state.idx_card_selected = this.get_idx_card_from_xy(xy);
 		this.selection_state.pos_from_selected = null;
 		this.selection_state.pos_to_selected = null;
 		this.selection_state.submit_button_state = null;
 		this.selection_state.idx_exchange_card_selected = null;
 	}

 	if(this.selection_state.idx_card_selected!=null) {
 		if(this.player_state.bool_card_exchanged) {

	     	// check exchange cards
	     	if(this.is_point_in_rect(xy, this.dict_area_rect[this.ID_AREA_EXCHANGE_CARDS].rect)) {
		     	this.selection_state.idx_exchange_card_selected = this.get_idx_exchange_card_from_xy(xy);
	     		if(this.selection_state.idx_exchange_card_selected!=null) {
	     			this.selection_state.submit_button_state = 1;
	     		}
	     	}

		    // chack balls		     		
	     	if(this.is_point_in_rect(xy, this.dict_area_rect[this.ID_AREA_BOARD].rect)) {

 				var pos = this.get_idx_pos_from_xy(xy);

	     		for(var i=0; i<this.CNT_POS; i++) {
	     			if(this.list_ball_selectable_from[i]) {
	     				if(pos==i) {
	     					this.selection_state.pos_from_selected = pos;
	     					this.selection_state.pos_to_selected = null;
	     					this.selection_state.submit_button_state = null;
	     					this.selection_state.exchange_card_visible = false;
	     				}
	     			}
	     			if(this.list_ball_selectable_to[i]) {
	     				if(pos==i && this.selection_state.pos_from_selected!=null) {
	     					this.selection_state.pos_to_selected = pos;
	     					this.selection_state.submit_button_state = 1
	     				}
	     			}
	     		}
     		}

 		} else {
 			this.selection_state.submit_button_state = 1;
 		}
 	}

 	// calc new slection
 	this.calc_selectable()

 	this.render();

}

Game.prototype.send_action_callback = function(action) {	
}

Game.prototype.can_select = function(e) {
 	return this.player_state==null || this.selection_state==null || this.player_state.idx_player_active!=this.player_state.idx_player_you;
}

Game.prototype.get_xy_from_cursor = function(e) {
 	var x = e.offsetX || (e.pageX - this.canvas.offsetLeft);
 	var y = e.offsetY || (e.pageY - this.canvas.offsetTop);
 	return [x, y];
}

Game.prototype.get_idx_card_from_xy = function(xy) {
 	var idx_card = null;
 	var player = this.player_state.list_player[this.idx_player_you];
 	for(var i=0; i<player.list_card.length; i++) {
 		if(!this.list_card_selectable[i]) {
 			continue;
 		}
 		var card = this.dict_player_card_rect.list_player[this.idx_player_you][i];
 		if(this.is_point_in_rect(xy, card)) {
 			idx_card = i;
 			break;
 		}
 	}
 	return idx_card;
}

Game.prototype.get_idx_exchange_card_from_xy = function(xy) {
 	var idx_card = null;
 	for(var i=0; i<this.dict_exchange_card_rect.length; i++) {
 		var card = this.dict_exchange_card_rect[i];
 		if(this.is_point_in_rect(xy, card.rect)) {
 			idx_card = i;
 			break;
 		}
 	}
 	return idx_card;
}

Game.prototype.get_id_button_from_xy = function(xy) {
	var button = this.dict_area_rect[this.ID_BUTTON_SUBMIT];
	if(this.is_point_in_rect(xy, button.rect)) {
		return this.ID_BUTTON_SUBMIT;
	}
 	return null;
}

Game.prototype.get_idx_pos_from_xy = function(xy) {
 	var idx_pos = null;
 	for(var i=0; i<this.CNT_POS; i++) {
 		var xy_pos = this.list_xy_pos_rotated[i];
 		if(this.is_point_in_circle(xy, xy_pos, this.r_active)) {
 			idx_pos = i;
 			break;
 		}
 	}
 	return idx_pos;
}

Game.prototype.is_point_in_rect = function(xy, rect) {
	return xy[0]>rect[0] && xy[0]<rect[0]+rect[2] && xy[1]>rect[1] && xy[1]<rect[1]+rect[3];
}
Game.prototype.is_point_in_circle = function(xy, xy_center, r) {
	return (xy[0]-xy_center[0])**2 + (xy[1]-xy_center[1])**2 < r**2;
}





Game.prototype.render = function () {
	if(!this.imgs_loaded || this.list_xy_pos_rotated==undefined) {
		return;
	}

	this.ctx.fillStyle = 'white';
	this.ctx.fillRect(0,0,this.canvas_width,this.canvas_height);

	var id_board = this.player_state==null ? 'board_0' : 'board_' + this.player_state.idx_player_you;
	this.ctx.drawImage(this.dict_imgs[id_board], this.board_x, this.board_y, this.board_width, this.board_width);

	this.ctx.strokeStyle = 'rgba(0,0,0,0.33)';
	this.ctx.lineWidth = 1;
	var r = this.board_width/50;
	for(var i=0; i<this.list_xy_pos_rotated.length; i++) {
		var xy = this.list_xy_pos_rotated[i];

		//position circles
		this.ctx.beginPath();
		this.ctx.arc(xy[0], xy[1], r, 0, 2 * Math.PI);
		this.ctx.stroke();
	}

	if(this.player_state==null) {
		return;
	}

	/*
	// inner circle
	this.ctx.beginPath();
	this.ctx.arc(this.board_center_x, this.board_center_y, 0.23*this.board_width, 0, 2 * Math.PI);
	this.ctx.stroke();

	// outer circle
	this.ctx.beginPath();
	this.ctx.arc(this.board_center_x, this.board_center_y, 0.57*this.board_width, 0, 2 * Math.PI);
	this.ctx.stroke();
	*/
	
	// active player
	if(!this.player_state.bool_game_finished) {
		this.ctx.font = '24px Arial';
		this.ctx.textBaseline = 'middle';
		var txt = this.player_state.list_player[this.player_state.idx_player_active].name + '\'s turn';
		if(this.player_state.idx_player_active==this.player_state.idx_player_you) {
			txt = 'Your Turn';
		}
		var w = this.ctx.measureText(txt).width/2;
		this.ctx.fillStyle = this.dict_players_colors[this.player_state.idx_player_active];
		this.ctx.fillText(txt, this.board_center_x-w, this.board_center_y-140);
	}

	// game state
	this.ctx.font = '24px Arial';
	this.ctx.textBaseline = 'middle';
	this.ctx.fillStyle = 'black';
	if(this.player_state.bool_game_finished) {
		var txt = 'Game Ended';
		var w = this.ctx.measureText(txt).width/2;
		this.ctx.fillText(txt, this.board_center_x-w, this.board_center_y+150);
	} else if(!this.player_state.bool_card_exchanged) {
		var txt = 'Exchange Cards';
		var w = this.ctx.measureText(txt).width/2;
		this.ctx.fillText(txt, this.board_center_x-w, this.board_center_y+150);
	}
	


	/**/
	// marbles image & shadow & save
	this.ctx.fillStyle = 'rgba(0,0,0,0.3)';
	this.ctx.lineWidth = 3;
	this.ctx.strokeStyle = 'black';
	var r_shadow = 0.022*this.board_width;
	for(var p=0; p<this.player_state.list_player.length; p++) {
		var player = this.player_state.list_player[p];
		for(var i=0; i<player.list_marble.length; i++) {
			var idx_pos = player.list_marble[i].pos;
			var is_save = player.list_marble[i].is_save;
			var xy = this.list_xy_pos_rotated[idx_pos];
			this.ctx.beginPath();
			this.ctx.arc(xy[0]+8, xy[1]+4, r_shadow, 0, 2 * Math.PI);
			this.ctx.fill();
			this.ctx.drawImage(this.dict_imgs['ball_'+player.idx_orig], xy[0]-19, xy[1]-19);

			if(is_save) {
				this.ctx.beginPath();
				this.ctx.arc(xy[0], xy[1], this.r_active*1.2, 0, 2 * Math.PI);
				this.ctx.stroke();
			}

		}

	}
	
	// selected marbles
	this.ctx.lineWidth = 3;
	for(var i=0; i<this.list_xy_pos_rotated.length; i++) {
		var xy = this.list_xy_pos_rotated[i];
		var is_selected = this.selection_state.pos_from_selected==i || this.selection_state.pos_to_selected==i;
		if(this.list_ball_selectable_from[i] || this.list_ball_selectable_to[i] || is_selected) {
			if(this.selection_state.idx_pos_hover==i || is_selected){
				this.ctx.strokeStyle = this.dict_colors[2];
			} else {
				this.ctx.strokeStyle = this.dict_colors[1];
			}
			this.ctx.beginPath();
			this.ctx.arc(xy[0], xy[1], this.r_active, 0, 2 * Math.PI);
			this.ctx.stroke();
		}
	}			

	// position nr
	if(this.config.debug) {
		this.ctx.textBaseline = 'middle';
		this.ctx.fillStyle = 'white';
		this.ctx.font = '14px Arial';
		this.ctx.lineWidth = 3;
		for(var i=0; i<this.list_xy_pos_rotated.length; i++) {
			var xy = this.list_xy_pos_rotated[i];
			var w = this.ctx.measureText(i).width;
			this.ctx.fillText(i, xy[0]-w/2, xy[1]);
		}			
	}

	// cards center
	var dim = this.dict_player_card_rect.card_stack;
	if(this.player_state.list_card_discard.length>0) {
		var card_stack = this.player_state.list_card_discard[this.player_state.list_card_discard.length-1];
		this.render_card(card_stack, dim[0], dim[1], dim[2], dim[3], 1, 0);			
	}
	dim = this.dict_player_card_rect.card_pile;
	this.render_card({suit:'', rank: 'BCK'}, dim[0], dim[1], dim[2], dim[3], 2, 0);


	// marble move direction
	if(this.selection_state.pos_from_selected!=null && this.selection_state.pos_to_selected!=null) {
		var xy_from = this.list_xy_pos_rotated[this.selection_state.pos_from_selected];
		var xy_to = this.list_xy_pos_rotated[this.selection_state.pos_to_selected];
		var d = Math.sqrt((xy_from[0]-xy_to[0])**2 + (xy_from[1]-xy_to[1])**2);
		var xy_from2 = [
			xy_from[0]+this.r_active*(xy_to[0]-xy_from[0])/d,
			xy_from[1]+this.r_active*(xy_to[1]-xy_from[1])/d
		];
		var xy_to2 = [
			xy_to[0]+this.r_active*(xy_from[0]-xy_to[0])/d,
			xy_to[1]+this.r_active*(xy_from[1]-xy_to[1])/d
		];

		this.ctx.strokeStyle = this.dict_colors[2];
		this.ctx.lineWidth = 3;
		this.ctx.beginPath();
		this.ctx.moveTo(xy_from2[0], xy_from2[1]);
		this.ctx.lineTo(xy_to2[0], xy_to2[1]);
		this.ctx.stroke();
	}


	// cards players
	var card_marked = false;
	for(var p=0; p<4; p++) {

		var is_active_and_you = this.player_state.idx_player_active==this.player_state.idx_player_you && p==this.idx_player_you;
		if(p%2==0) {
			for(var i=0; i<this.player_state.list_player[p].list_card.length; i++) {
				var card = this.player_state.list_player[p].list_card[i];
				var rect = this.dict_player_card_rect.list_player[p][i];
				var status = is_active_and_you && this.list_card_selectable[i] ? (i==this.selection_state.idx_card_hover || i==this.selection_state.idx_card_selected ? 2 : 1) : 0;
				var elevation = is_active_and_you && i==this.selection_state.idx_card_selected && !this.player_state.bool_card_exchanged ? -25 : 0;
				if(this.config.spectator && !card_marked && this.player_state.selected_action!=null && this.are_cards_equal(this.player_state.selected_action.card, card) && p==this.player_state.idx_player_active) {
					status = 1;
					card_marked = true;
				}
				this.render_card(card, rect[0], rect[1]+elevation, rect[2], rect[3], 0, status);
				/*
				if(this.config.spectator && p!=this.player_state.idx_player_active) {
					this.ctx.fillStyle = 'rgba(255,255,255,0.66)';
					this.ctx.fillRect(rect[0], rect[1], rect[2], rect[3]);
				}
				*/
			}
			if(this.player_state['list_player_names']!=undefined) {
				this.ctx.font = '24px Arial';
				this.ctx.textBaseline = 'middle';
				var txt = this.player_state['list_player_names'][p];
				var w = this.ctx.measureText(txt).width/2;
				this.ctx.fillStyle = 'black';
				var offset = (1-p)*(this.board_width/2+22);
				this.ctx.fillText(txt, this.board_center_x-w, this.board_center_y+offset);
			}
		} else {
			this.ctx.save();
			this.ctx.translate(this.board_center_x, this.board_center_y);
			this.ctx.rotate(-Math.PI / 2);
			for(var i=0; i<this.player_state.list_player[p].list_card.length; i++) {
				var card = this.player_state.list_player[p].list_card[i];
				var rect = this.dict_player_card_rect.list_player[p][i];
				var status = is_active_and_you && this.list_card_selectable[i] ? (i==this.selection_state.idx_card_hover || i==this.selection_state.idx_card_selected ? 2 : 1) : 0;
				var elevation = is_active_and_you && i==this.selection_state.idx_card_selected && !this.player_state.bool_card_exchanged ? -25 : 0;
				if(this.config.spectator && !card_marked && this.player_state.selected_action!=null && this.are_cards_equal(this.player_state.selected_action.card, card) && p==this.player_state.idx_player_active) {
					status = 1;
					card_marked = true;
				}
				this.render_card(card, -rect[1]+this.board_center_y-rect[3]+elevation, rect[0]-this.board_center_x, rect[3], rect[2], -1, status);
				/*
				if(this.config.spectator && p!=this.player_state.idx_player_active) {
					this.ctx.fillStyle = 'rgba(255,255,255,0.66)';
					this.ctx.fillRect(-rect[1]+this.board_center_y-rect[3], rect[0]-this.board_center_x, rect[3], rect[2]);
				}
				*/
			}
			this.ctx.restore();
			if(this.player_state['list_player_names']!=undefined) {
				this.ctx.save();
				this.ctx.translate(this.board_center_x, this.board_center_y);
				this.ctx.rotate(Math.PI / 2);
				this.ctx.font = '24px Arial';
				this.ctx.textBaseline = 'middle';
				var txt = this.player_state['list_player_names'][p];
				var w = this.ctx.measureText(txt).width/2;
				this.ctx.fillStyle = 'black';
				var offset = (2-p)*(this.board_width/2+22);
				this.ctx.fillText(txt, -w/2, offset);
				this.ctx.restore();
			}
		}
	}

	// exchange chards
	if(this.selection_state.exchange_card_visible) {
		if(this.selection_state.idx_exchange_card_selected==null) {
			for(var i=0; i<this.dict_exchange_card_rect.length; i++) {
				var card_exchange = this.dict_exchange_card_rect[i];
				var rect = card_exchange.rect;
				var status = i==this.selection_state.idx_exchange_card_hover || i==this.selection_state.idx_exchange_card_selected ? 2 : 1;
				this.render_card(card_exchange.card, rect[0], rect[1], rect[2], rect[3], 0, status);
			}
		} else{
			var card = this.player_state.list_player[this.idx_player_you].list_card[this.selection_state.idx_card_selected];
			var rect = this.dict_player_card_rect.list_player[this.idx_player_you][this.selection_state.idx_card_selected];
			var card_exchange = this.dict_exchange_card_rect[this.selection_state.idx_exchange_card_selected];
			this.render_card(card_exchange.card, rect[0]+card_exchange.rect[2]/2, rect[1]+card_exchange.rect[3]/2, card_exchange.rect[2], card_exchange.rect[3], 0, 2);
		}
	}


	// submit button
	if(this.selection_state.submit_button_state!=null) {
		// game state
		var button = this.dict_area_rect[this.ID_BUTTON_SUBMIT];
		var rect = button.rect;
		this.ctx.font = button.f+'px Arial';
		this.ctx.fillStyle = 'rgba(0,0,0,0.2)';
		this.ctx.fillRect(rect[0]+5, rect[1]+10, rect[2], rect[3]);

		this.ctx.fillStyle = 'white';
		this.ctx.strokeStyle = this.dict_colors[this.selection_state.submit_button_state];
		this.ctx.fillRect(rect[0], rect[1], rect[2], rect[3]);
		this.ctx.strokeRect(rect[0], rect[1], rect[2], rect[3]);
		this.ctx.fillStyle = 'black';
		this.ctx.textBaseline = 'top';
		this.ctx.textAlign = 'left';
		this.ctx.fillText(button.txt, rect[0]+button.dx, rect[1]+button.dy);
	}
	
	if(false) {
		// areas
		this.ctx.lineWidth = 1;
		this.ctx.strokeStyle = 'red';
		for (const [key, button] of Object.entries(this.dict_area_rect)) {
			var rect = button.rect;
			this.ctx.strokeRect(rect[0], rect[1], rect[2], rect[3]);
		}
	}

}

Game.prototype.render_card = function (card, x, y, w, h, shadow_type, status) {
	var id_card = this.get_id_from_card(card);
	this.ctx.fillStyle = 'rgba(0,0,0,0.2)';
	var r = 5;
	if(shadow_type==2) {
		var dx = 40;
		var dy = 20;
		this.ctx.beginPath();
		this.ctx.moveTo(x+w-2, y+1);
		this.ctx.lineTo(x+w-2+dx-4, y+1+dy);
		this.ctx.lineTo(x+w-2+dx-2, y+1+dy+2);
		this.ctx.lineTo(x+w-2+dx, y+1+dy+4);
		this.ctx.lineTo(x+w-2+dx, y+1+dy/2+h);
		this.ctx.arc(x+w-2+dx-r, y+1+dy/2+h-r, r, 0, Math.PI/2);
		this.ctx.lineTo(x+4+dx*1.5, y+1+dy/2+h);
		this.ctx.lineTo(x+4,y+h);
		this.ctx.closePath();
		this.ctx.fill();
	} else {
		var dx = 3;
		var dy = 2;
		if(shadow_type==-1) {
			dx = -2;
			dy = 3;				
		}
		this.ctx.beginPath();
		this.ctx.arc(dx+x+w-r, dy+y+r, r, -Math.PI/2, 0);
		this.ctx.arc(dx+x+w-r, dy+y+h-r, r, 0, Math.PI/2);
		this.ctx.arc(dx+x+r, dy+y+h-r, r, Math.PI/2, Math.PI);
		this.ctx.arc(dx+x+r, dy+y+r, r, Math.PI, 3*Math.PI/2);
		this.ctx.closePath();
		this.ctx.fill();
		if(shadow_type==1) {
			this.ctx.fillStyle = 'white';
			this.ctx.fillRect(x, y+h, 33, dy);
		}
	}
	this.ctx.drawImage(this.dict_imgs['card_'+id_card], x, y, w, h);

	if(status>0) {
		var p = 2;
		r = 8;
		this.ctx.strokeStyle = this.dict_colors[status];
		this.ctx.lineWidth = 3;
		this.ctx.beginPath();
		this.ctx.arc(x+p+w-r, y-p+r, r, -Math.PI/2, 0);
		this.ctx.arc(x+p+w-r, y+p+h-r, r, 0, Math.PI/2);
		this.ctx.arc(x-p+r, y+p+h-r, r, Math.PI/2, Math.PI);
		this.ctx.arc(x-p+r, y-p+r, r, Math.PI, 3*Math.PI/2);
		this.ctx.closePath();
		this.ctx.stroke();
	}
}