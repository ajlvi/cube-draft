var dataDump = null;
var reservedid = -1;
var timer = null;
var vertbardone = false;

function ping() {
	$.get('/makepick', {draftid : thisdraft, player : thisplayer, pickid : -1}, function(response) {
		dataDump = response;
		if (!vertbardone) {
			vertBar(dataDump['total_packs'], dataDump['cards_per_pack']);
		}
		updatePicks(); //update the list of existing picks
		if (response['my_status']==0) {
			$('#packdisp').html('waiting....') //change this later
			setTimeout(function() {ping(); }, 2000);
			}
		else {
			//this means we have to populate the table!
			reservedid = response['current_pack'][0];
			populateTable(response['current_pack'],response['current_df']);
			setTimer(response['time_remaining']);
			} 
		});
	};

function updatePicks() {
	//for each card in the cardlist, we'll determine the pack and pick number, then get a string of html, then insert it
	var cardlist = dataDump['chosen_cards']
	var packs = dataDump['total_packs']
	var picks = dataDump['cards_per_pack']
	var thispack = 1;
	var thispick = 1;
	for (cardidx=0; cardidx<cardlist.length; cardidx++) {
		makeJSPick(cardlist[cardidx], thispack, thispick);
		if (thispick < picks) {thispick++;}
		else {thispick = 1; thispack++;}
	}
};


function setTimer(time) {
	i = Math.floor(time);
	timer = setInterval(function() {runTimer(i);}, 1000);
};
	
function runTimer(num) {
	if (num > 0) {
		min = Math.floor(num/60);
		sec = num - min*60;
		if (sec < 10) {secstring = '0'+ sec.toString();}
		else {secstring = sec.toString();}
		$("#timer").text(min.toString() + ':' + secstring);
		i--;
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
	if (k < 7) {
		while(k < 8) {
			outstring = outstring + '<td class="pick-table-cell empty"></td>' ;
			k++;	
		}
		outstring = outstring + '</tr><tr class="pick-table-row"><td class="pick-table-cell empty" colspan=7></td>' ;
	}
	else if (k < 15) {
		outstring = outstring + '<td class="pick-table-cell empty" colspan=' + (15-k).toString() + '></td>' ;
	}
	outstring = outstring + '<td class="pick-table-cell buttonbox"><button id="confirm">confirm pick</button></tr>';
	$("#packdisp").html(outstring);
	initializePack();
};

function initializePack() {
	$("#confirm").click(function(){
		makePick(thisplayer, thisdraft, reservedid);
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
			var cardname = $(this).attr("name");
			var cardid = $(this).attr("id");
			$(this).addClass("unreserved");
			$(this).removeClass("reserved");
			makePick(thisplayer, thisdraft, cardid);
		}); 
	}) ;
};


//a function for actually making a pick -- sends player name, draft id, pick number
function makePick(playername, dnum, pnum) {
		clearInterval(timer);
		$.get('/makepick', {player : playername, draftid: dnum, pickid: pnum}, function(response) {
		reservedid = -1;
		dataDump = response;
		updatePicks(); //update the list of existing picks
		if (response['my_status']==0) {
			$('#packdisp').html('wait!!'); //change this later
			setTimeout(function() {ping(); }, 2000);
			}
		else {
			//this means we have to populate the table!
			reservedid = response['current_pack'][0];
			populateTable(response['current_pack'],response['current_df']);
			setTimer(response['time_remaining']);
			} 
		});	
};