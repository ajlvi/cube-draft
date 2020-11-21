var dataDump = null;
var reservedid = -1;
var timer = null;
var vertbardone = false;
var draftover = false;
var startTime = null;

function ping() {
	$.get('/makepick', {draftid : thisdraft, player : thisplayer, pickid : -1, isCogwork : 'no'}, function(response) {
		dataDump = response;
		if (!vertbardone) {
			var tossed = dataDump['thrown_picks'] ;
			vertBar(dataDump['total_packs'], dataDump['cards_per_pack'] - tossed);
		}
		updatePicks(); flowBar() //update the list of existing picks
		if (response['my_status']==0) {
			//0: wait for picks; 1: wait for players; 2: modo export message
			if (dataDump.packno == 0) { $('#packdisp').html(midTableMessage(1)) ; }
			else if (dataDump.chosen_cards.length == dataDump.total_packs * (dataDump.cards_per_pack 0 dataDump.thrown_picks)) { $('#packdisp').html(midTableMessage(2)); draftover=true;}
			else {$('#packdisp').html(midTableMessage(0)) ; }
			if (!draftover) {setTimeout(function() {ping(); }, 2000);}
			}
		else {
			//this means we have to populate the table!
			reservedid = response['current_pack'][0];
			populateTable(response['current_pack'],response['current_df']);
			setTimer(response['time_remaining']);
			packAndPickNos();
			} 
		});
	};
	
function midTableMessage(choice) {
	//returns a string meant to be plugged into the table.
	if (choice == 0) { return '<tr class="fulltr"><td class="fulltd">Waiting for a player to pick a card.</tr>' ;}
	else if (choice == 1) { return '<tr class="fulltr"><td class="fulltd">Waiting for players to join the draft.</tr>' ;}
	else if (choice == 2) {
		var outstring = '<tr class="fulltr"><td class="fulltd">' ;
		outstring = outstring + "The draft has ended. Use the following button to export your pool as a Magic Online .dek file.";
		outstring = outstring + "<br>If you have cards in the bottom panel, the rest of your pool will be put in the sideboard.";
		outstring = outstring + "<br>If the bottom panel is empty, all of your cards will appear in the main deck."
		outstring = outstring + "<br><br><button class='modobutton' onClick='javascript:MODOExport()'>export</button></td></tr>";
		return outstring
	}
	else { return '' ;}
}

function updatePicks() {
	//for each card in the cardlist, we'll determine the pack and pick number, then get a string of html, then insert it
	var cardlist = dataDump['chosen_cards']
	var tossed = cutCards(dataDump["total_packs"], dataDump["cards_per_pack"], dataDump["drafters"].length, dataDump["scheme"]) ;
	var packs = dataDump['total_packs']
	var picks = dataDump['cards_per_pack']
	var thispack = 1;
	var thispick = 1;
	for (cardidx=0; cardidx<cardlist.length; cardidx++) {
		makeJSPick(cardlist[cardidx], thispack, thispick);
		if (thispick < picks - tossed) {thispick++;}
		else {thispick = 1; thispack++;}
	}
	addSideOverlays();
};


function setTimer(time) {
	var d = new Date();
	startTime = d.getTime();
	timeFloor = Math.floor(time);
	timer = setInterval(function() {runTimer(timeFloor);}, 1000);
};
	
function runTimer(num) {
	if (num > 0) {
		min = Math.floor(num/60);
		sec = num - min*60;
		if (sec < 10) {secstring = '0'+ sec.toString()}
		else {secstring = sec.toString();}
		if (num < 3) {var bgcolor = " panic"}
		else if (num < 10) {var bgcolor = " low-time" }
		else {var bgcolor = ""}
		$("#timer").html("<span class='timebox" + bgcolor + "'>" + min.toString() + ':' + secstring + "</span>");
		timeFloor--;
	}
	else if (num==0) {
		makePick(thisplayer, thisdraft, reservedid);
	}
};

function populateTable(cardlist, cardinfo) {
	//this should take a response that contains a new pack and populate the table with it
	//we need to make a cell for each card
	cardinfo = JSON.parse(cardinfo);
	outstring = ''
	for (j=0; j<cardlist.length; j++) {
		if (j==0) {outstring = outstring + "<tr class='pick-table-row'>" };
		var cardid = cardlist[j].toString();
		var name = cardinfo['card'][cardlist[j]];
		var imgsrc = cardinfo['scryfall'][cardlist[j]];
		outstring = outstring + '<td class="pick-table-cell"><img src="' + imgsrc + '" class="card-image unreserved" name="' + name + '" id="' + cardid + '"></td>';
		if (j==7) {outstring = outstring + "</tr>\n<tr class='pick-table-row'>";}
	}
	/* we're done writing the cards; now include empty cells to fill out table */
	var k = cardlist.length;
	if (k < 8) {
		while(k < 8) {
			outstring = outstring + '<td class="pick-table-cell empty"></td>' ;
			k++;	
		}
		outstring = outstring + '</tr><tr class="pick-table-row"><td class="pick-table-cell empty" colspan=7></td>' ;
	}
	else if (k < 15) {
		outstring = outstring + '<td class="pick-table-cell empty" colspan=' + (15-k).toString() + '></td>' ;
	}
	// last cell -- button either with or without librarian
	if (dataDump.has_cogwork == dataDump.my_name) {
		outstring = outstring + '<td class="pick-table-cell buttonbox"><div class="cogwork-button"><button id="cogwork">replace with<br> librarian</button></div><div class="regular-button"><button id="confirm">confirm pick</button></div></tr>';
	}
	else {
		outstring = outstring + '<td class="pick-table-cell buttonbox"><div class="regular-button"><button id="confirm">confirm pick</button></div></tr>';
	}
	$("#packdisp").html(outstring);
	initializePack();
};

function initializePack() {
	$("#confirm").click(function(){
		var rightNow = new Date();
		if (rightNow.getTime() - startTime > 1500) {
			makePick(thisplayer, thisdraft, reservedid); }
	});
	$("#cogwork").click(function(){
		var rightNow = new Date();
		if (rightNow.getTime() - startTime > 1500) {
			makePick(thisplayer, thisdraft, reservedid, 'yes'); }
	});
	$(".unreserved").click(function(){
		$(".card-image").not(this).removeClass("reserved");
		$(".card-image").not(this).addClass("unreserved");
		$(".card-image").not(this).off("dblclick");
		$(this).removeClass("unreserved");
		$(this).addClass("reserved");
		reservedid = $(this).attr("id");
		$(this).off("dblclick");
		$(this).dblclick(function(){
			var rightNow = new Date();
			if (rightNow.getTime() - startTime > 1500) {
			var cardname = $(this).attr("name");
			var cardid = $(this).attr("id");
			$(this).addClass("unreserved");
			$(this).removeClass("reserved");
			makePick(thisplayer, thisdraft, cardid);
			}
		}); 
	}) ;
	$('.card-image').bind('contextmenu', function(e) {
		return false;
	}); 
	$(".card-image").mousedown(function(e) {
		if (e.which > 1) {
			var zoomIn = true; 
			var my_src = $(this).attr('src');
			var zb = $("#zoom-box");
			if (zb.children("img").length > 0) {
				var zoom_src = zb.children("img")[0].src ;
				if (zoom_src == my_src) {
					zoomIn = false ;
					zb.html('') ;
				}
			}
			if (zoomIn) {
				var img_tag = '<img src="' + my_src + '" class="zoomed-image">';
				var my_id = parseInt($(this).attr('id'));
				if (JSON.parse(dataDump.current_df)["back"][my_id] != null) {
					back_src = JSON.parse(dataDump.current_df)["back"][my_id];
					img_tag = img_tag + '<img src="' + back_src + '" class="zoomed-image">';
				}
				zb.html(img_tag) ;
			}
		}
	});
};


//a function for actually making a pick -- sends player name, draft id, pick number
function makePick(playername, dnum, pnum, cogwork='no') {
		clearInterval(timer);
		$.get('/makepick', {player : playername, draftid: dnum, pickid: pnum, isCogwork: cogwork}, function(response) {
		reservedid = -1;
		dataDump = response;
		updatePicks(); //update the list of existing picks
		packAndPickNos(); //clear the pack and pick numbers
		$('#zoom-box').html(''); //in case any card image was zoomed in
		$('#timer').html('');
		if (response['my_status']==0) {
			$('#packdisp').html(midTableMessage(0)); //change this later
			setTimeout(function() {ping(); }, 2000);
			}
		else {
			//this means we have to populate the table!
			reservedid = response['current_pack'][0];
			flowBar(); //we got some data back so we'll update what we know
			populateTable(response['current_pack'],response['current_df']);
			setTimer(response['time_remaining']);
			} 
		});	
};

function packAndPickNos() {
	var tossed = cutCards(dataDump["total_packs"], dataDump["cards_per_pack"], dataDump["drafters"].length, dataDump["scheme"]) ;
	var pick_no = (1 + dataDump.chosen_cards.length) % (dataDump.cards_per_pack-tossed)
	if (pick_no == 0) {pick_no = (dataDump.cards_per_pack-tossed) ;}
	if (dataDump.current_pack == null) { var packstring = '' ; var pickstring = '' ;}
	else { 
		var packstring = 'pack <span class="pack-no">' + dataDump.packno.toString() + '</span>' ;
		var pickstring = 'pick <span class="pick-no">' + pick_no.toString() + '</span>' ;
	}
	$('#pack-number').html(packstring);
	$('#pick-number').html(pickstring);
}

//adds overlays to the picks panel this needs to be re-run when new picks are added.
function addSideOverlays() {
	$(".tooltip").mouseenter(function(event){
		if ($(this).parent('span').children('span.image-overlay').length) {
			$(this).parent('span').children('span.image-overlay').show();
		} else {
			var image_name = $(this).data('image');
			var imageTag='<span class="image-overlay" style="position:absolute;">' + '<img src="' + image_name + '" alt="image-overlay" height="300" />' + '</span>';
			$(this).parent('span').append(imageTag);
			
			var rightWidth = ($(this).width() + 2).toString() + "px"
			$(this).parent('span').children('span.image-overlay').css("right", rightWidth); 
			
			if ( $(this).parent('span').position()["top"] + 320 > $(window).height() ) {
				$(this).parent('span').children('span.image-overlay').css("bottom", "16px"); }
			else { $(this).parent('span').children('span.image-overlay').css("top", "16px"); }
			
			$(this).parent('span').children('span.image-overlay').css("z-index", "1");
		}
	});

	$(".tooltip").mouseleave(function(){
		$(this).parent('span').children('span.image-overlay').hide();
    });
};