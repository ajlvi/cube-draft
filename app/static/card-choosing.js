var deck = [] ;

var costdict = {"W/U": "azorius", "U/B": "dimir", "B/R": "rakdos", "R/G": "gruul", "G/W": "selesnya", "W/B": "orzhov", "B/G": "golgari", "G/U": "simic", "U/R": "izzet", "R/W": "boros", "W/P": "phw", "U/P": "phu", "B/P": "phb", "R/P": "phr", "G/P": "phg"};

function getCost(cardnum) {
	return JSON.parse(dataDump["chosen_df"])["cost"][cardnum];
}

function getName(cardnum) {
	return JSON.parse(dataDump["chosen_df"])["card"][cardnum];
}

function isCreature(cardnum) {
	return JSON.parse(dataDump["chosen_df"])["creature"][cardnum] == 1
}

/* note this either returns a single string or a list for split cards.*/
function manaSpan(cost, loc, slashed=false) {
	if (cost == null) { return "<span class='mana-" + loc + "'></span>" ; }
	else if (cost.indexOf("//") == -1) {
		splitcost = cost.slice(1, cost.length-1).split("}{")
		if (slashed) { var slash = "-slashed" ; } else { var slash = '' ; }
		var mana = "<span class='mana-" + loc + slash + "'>"
		for (j=0; j<splitcost.length; j++) {
			symb = splitcost[j]
			if (symb in costdict) {
				mana = mana + '<img src="/static/symbols/' + costdict[symb] + '.png" class="symbolimg-' + loc + '">';}
			else if (["W", "U", "B", "R", "G"].indexOf(symb) >= 0)
				{mana = mana + '<img src="/static/symbols/' + symb + '.png" class="symbolimg-' + loc + '">' }
			else if ( symb == "X" ) {mana = mana + '<img src="/static/symbols/genx.png" class="symbolimg-' + loc + '">'}
			else {mana = mana + '<img src="/static/symbols/gen' + symb + '.png" class="symbolimg-' + loc + '">'}
		}
		return mana
	}
	else { costs = cost.split(" // ");
		return [manaSpan(costs[0], loc, true), manaSpan(costs[1], loc, true)];
	}
} 

function cardString(cardnum) {
	var cardname = getName(cardnum) ;
	var cost = getCost(cardnum) ;
	var arrows = '<span class="arrows"><a href="javascript:addToDeck(' 	+ cardnum + ')" class="addlink">▼</a><a href="javascript:pullFromDeck(' + cardnum + ')" class="droplink">▲</a></span>'
	var manacost = manaSpan(cost, 'vert');

	if (cardname.indexOf("//") == -1 | cardname.includes("Pathway")) {
		if (manacost.split(".png").length > 4) {var bufferspace = ' style="padding:0px 0px 0px 4px"';}
		else {var bufferspace = '';}
		return arrows + manacost + '</span><span class="cardname"' + bufferspace + '><a class="tooltip" href="javascript:addToDeck(' + cardnum + ')" data-image="' + JSON.parse(dataDump.chosen_df)["scryfall"][cardnum] + '">' + cardname + '</a></span>'
	}
	else {
		var bufferspace = ' style="padding:0px 0px 0px 4px"';
		return arrows + manacost[0] + '</span><span class="slashspan">//</span>' + manacost[1] + '</span><span class="cardname"' + bufferspace + '><a class="tooltip" href="javascript:addToDeck(' + cardnum + ')" data-image="' + JSON.parse(dataDump.chosen_df)["scryfall"][cardnum] + '">' + cardname + '</a></span>'
	}
} ;

/*		this code is for [COST 1} card 1 // [COST 2] card 2
		if (firstcost.split(".png").length > 4) {var bufferspace = ' style="padding:0px 0px 0px 4px"';}
		else {var bufferspace = '';}
		outstring = arrows + firstcost + '</span><span class="cardname"' + bufferspace + '>' + cardnames[0] + '</span><span class="slashspan">//</span>'
		
		secondcost = manacost[1]
		if (secondcost.split(".png").length > 4) {var bufferspace = ' style="padding:0px 0px 0px 4px"';}
		else {var bufferspace = '';}
		outstring = outstring + secondcost + '</span><span class="cardname"' + bufferspace + '>' + cardnames[1] + '</span>'
		return outstring
*/

function cmc(cardnum) {
	var cost = getCost(cardnum);
	var cardname = getName(cardnum); 
	if (cost == null) {return 1;}
	if (cardname.indexOf("//") != -1) { cost = cost.split(" // ")[0] ; }
	if (cost.indexOf("}{") == -1) {
		if (parseInt(cost[1]) > 0) { return Math.min(6, parseInt(cost[1])); }
		else { return 1 ; }
	}
	var splitcost = cost.slice(1, cost.length-1).split("}{")
	var total = 0 ;
	for (j=0; j<splitcost.length; j++) {
		if (parseInt(cost[j]) > 0) { total = total + parseInt(cost[j]); }
		else if (cost[j] == "X") {total = total + 6 ;}
		else { total++ ; }
	}
	if (total >= 6) {return 6;}
	return total;
}

function makeJSPick(cardnum, packno, pickno) {
	var pickdiv = document.getElementById("pick-" + packno + "-" + pickno) ;
	pickdiv.innerHTML = cardString(cardnum) ;
	
//change the length of the cardname box, if needed, to avoid wrapping
	var tot = 246 ;
	var spans = $(pickdiv).children() ;
	var i = 0 ;
	while (!$(spans[i]).hasClass("cardname")) {
		tot = tot - $(spans[i]).width() ; 
		if ($(spans[i]).hasClass("slashspan")) { tot = tot - 6 ; }
		if ($(spans[i]).hasClass("arrows")) { tot = tot - 6 ; }
		i ++; }
	if ( tot < 170 ) { $(spans[i]).css("max-width", tot) ;}
}
	
//functions below have to do with moving the cards to and from the deck 
	
function addToDeck(cardnum) {
	if (deck.indexOf(cardnum) == -1) {
	deck.push(cardnum) ; writeCMCs() ; }
}

function pullFromDeck(cardnum) {
	var idx = deck.indexOf(cardnum);
	deck.splice(idx, 1); writeCMCs() ;
}

function writeCard(cardnum) { 
	var cardcmc = cmc(cardnum);
	var creatureQ = isCreature(cardnum) ;
	var cardname = getName(cardnum) ;
	if (creatureQ) { var spanid = "creatures-" + cardcmc ; }
	else { var spanid = "noncreatures-" + cardcmc ; }
	var docspan = document.getElementById(spanid) ;
	var current = docspan.innerHTML;
	var present = '<div class="bottom-card">'
	var manacost = manaSpan(getCost(cardnum), "bot")
	if (cardname.indexOf("//") != -1 & !cardname.includes("Pathway")) {manacost = manacost[0]; }
	if (manacost.split(".png").length > 4) {
		var bufferspace = ' style="padding:0px 0px 0px 3px"';}
	else {var bufferspace = '';}
	present = present + manacost + '</span><span class="cardname-bot"' + bufferspace + '><a href="javascript:pullFromDeck(' + cardnum + ')">' + cardname + '</a></span></div>'
	docspan.innerHTML = current + present ;
}

function writeCMCs() {
	//cogwork nonsense -- is there a card in the deck not in our pool?
	var df = JSON.parse(dataDump.chosen_df).card
	var cutIdx = []
	for (draftedCardIndex=0; draftedCardIndex < deck.length; draftedCardIndex++) {
		if (!(deck[draftedCardIndex] in df)) { cutIdx.push(draftedCardIndex) }
	}
	if (cutIdx.length == 1) { deck.splice(cutIdx[0], 1); }
	//okay whew, now let's write all the cards in the deck.
	for (j=1; j<=6; j++) {
		cspan = document.getElementById("creatures-" + j);
		nspan = document.getElementById("noncreatures-" + j);
		cspan.innerHTML = ''; nspan.innerHTML = ''
	}
	for (k=0; k<deck.length; k++) {
		writeCard(deck[k]);
	}
}

/* these functions were used for the stream draft overlay and are not used presently. 

function writeCMCs() {
	cols = {"creatures-1": [], "creatures-2": [], "creatures-3": [], "creatures-4": [],
			"creatures-5": [], "creatures-6": [], "noncreatures-1": [], "noncreatures-2": [],
			"noncreatures-3": [],"noncreatures-4": [],"noncreatures-5": [],"noncreatures-6": []};
	var sidebar = document.getElementById("side-string");
	var sidedata = eval("[" + sidebar.value + "]") ;
	for (k=1; k < 43; k++) {
		var cardno = picked[k] ;
		if (cardno != 0 && !sidedata.includes(k)) {
			cmcOfCard = cmc(cardno) ;
			isCreature = data[cardno][2] ;
			if (isCreature == 1) { var label = "creatures-" + cmcOfCard ;}
			else { var label = "noncreatures-" + cmcOfCard ;}
			cols[label].push(cardString(cardno) + "<br>");
		}
	}
	for (j=1; j < 7; j++) {
		var clabel = "creatures-" + j;
		var nlabel = "noncreatures-" + j;
		var cout = '';
		var nout = '';
		for (s = 0; s < cols[clabel].length; s++)
			{ cout = cout + cols[clabel][s] ; }
		for (s = 0; s < cols[nlabel].length; s++)
			{ nout = nout + cols[nlabel][s] ; }
		var creat = document.getElementById(clabel) ;
		var noncreat = document.getElementById(nlabel);
		creat.innerHTML = cout;
		noncreat.innerHTML = nout;
	}
}

function draftCard() {
	var picknum = document.getElementById("pick-number-menu") ;
	var curcard = document.getElementById("card-choice-menu") ;
	makePick(curcard.value, picknum.value) ;
	postRecovery()
	picknum.value++;
}

function postRecovery() {
	recover = ""
	for (k=1; k<43; k++) {
		if (picked[k] != 0) {recover = recover + k + ":" + picked[k] + ";" ; } }
	var recoverbar = document.getElementById("recovery-string") ;
	recoverbar.value = recover.slice(0, recover.length-1) ;
}

function recovery() {
	var recoverbar = document.getElementById("recovery-string") ;
	var rawstring = recoverbar.value
	var picks = rawstring.split(";")
	for (i=0; i<picks.length; i++) {
		vals = picks[i].split(":");
		makePick( parseInt(vals[1]), parseInt(vals[0]) );
	}
}

function sideboard() {
	var sideInput = document.getElementById("side-string");
	var sidelist = eval("[" + sideInput.value + "]");
	for (k=0; k<sidelist.length; k++)
		{ var cardslot = document.getElementById("pick-" + sidelist[k]) ;
		  cardslot.style.color = '#AAAAAA' ; }
	writeCMCs() ;
}

*/