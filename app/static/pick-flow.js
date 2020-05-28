var datadump = null;

function ping() {
	$.get('/makepick', function(response) {
		dataDump = response;
		updatePicks(response); //update the list of existing picks
		if (response['my_status']==0) {
			setTimeout(function() {ping(); }, 2000);
			}
		else {
			//this means we have to populate the table!
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
	for (j=0; j<cardlist.length; j++) {
		makeJSPick(cardlist[j], thispack, thispick);
		if (thispick < picks) {thispick++;}
		else {thispick = 1; thispack++;}
	}
};


function setTimer(time) {
	i = Math.floor(time);
	setInterval(function() {runTimer(i);}, 1000);
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
		//makePick(cardname, pack, pick);
		$("#timer").text('time is up!');
		}
	};

function populateTable(cardlist,cardinfo) {
	//this should take a response that contains a new pack and populate the table with it
	//we need to make a cell for each card
	cardinfo = JSON.parse(cardinfo);
	for (j=0; j<cardlist.length; j++) {
		cardid = cardlist[j].toString();
		name = cardinfo['card'][cardlist[j]];
		imgsrc = cardinfo['scryfall'][cardlist[j]];
		$("#packdisp").append('<td><img src="' + imgsrc + '" class="card-image unreserved" name="' + name + '" id="' + cardid + '"></td>');
	}
	initializePack();
};

function initializePack() {
	$(".unreserved").click(function(){
		$(".card-image").not(this).removeClass("reserved");
		$(".card-image").not(this).addClass("unreserved");
		$(".card-image").not(this).off("dblclick");
		$(this).removeClass("unreserved");
		$(this).addClass("reserved");
		$(this).off("dblclick");
		$(this).dblclick(function(){
			var cardname = $(this).attr("name");
			var cardid = $(this).attr("id");
			makePick(cardid, player);
			//if (pick < 15) {pick++;}
			//else {pick = 1; pack++;}
			$(this).addClass("unreserved");
			$(this).removeClass("reserved");
		}); 
	}) ;
};