var deck = [] ;
var picked = {} ;

var costdict = {"W/U": "azorius", "U/B": "dimir", "B/R": "rakdos", "R/G": "gruul", "G/W": "selesnya", "W/B": "boros", "B/G": "golgari", "G/U": "simic", "U/R": "izzet", "R/W": "boros"};

function getCost(cardname) {
	if (cardname == "Favored Hoplite") {return "{W}";}
	else if (cardname == "Lagonna-Band Trailblazer") {return "{W}";}
	else if (cardname == "Thraben Inspector") {return "{W}";}
	else if (cardname == "Aviary Mechanic") {return "{1}{W}";}
	else if (cardname == "Hero of Iroas") {return "{1}{W}";}
	else if (cardname == "Seeker of the Way") {return "{1}{W}";}
	else if (cardname == "Serene Steward") {return "{1}{W}";}
	else if (cardname == "Syndic of Tithes") {return "{1}{W}";}
	else if (cardname == "Phalanx Leader") {return "{W}{W}";}
	else if (cardname == "Angel of Vitality") {return "{2}{W}";}
	else if (cardname == "Avacynian Missionaries") {return "{3}{W}";}
	else if (cardname == "Decree of Justice") {return "{X}{X}{2}{W}{W}";}
	else if (cardname == "Commit // Memory") {return "{3}{U} // {4}{U}{U}"}
	else if (cardname == "Arcanist's Owl") {return "{W/U}{W/U}{W/U}{W/U}"}
	else if (cardname == "Temmet, Vizier of Naktamun") {return "{W}{U}";}
	return 'nan'
}

function isCreature(cardname) {
	if (cardname == "Decree of Justice") {return false;}
	else if (cardname == "Commit // Memory") {return false;}
	return true;
}

/* note this either returns a single string or a list for split cards.*/
function manaSpan(cost, loc) {
	if (cost == "nan") { mana = "<span class='mana-" + loc + "'>&nbsp;</span>" ; }
	else if (cost.indexOf("//") == -1) {
		splitcost = cost.slice(1, cost.length-1).split("}{")
		var mana = "<span class='mana-" + loc + "'>"
		for (j=0; j<splitcost.length; j++) {
			symb = splitcost[j]
			if (symb in costdict) {
				mana = mana + '<img src="/static/symbols/' + costdict[symb] + '.png" class="symbolimg-' + loc + '">';}
			else if (["W", "U", "B", "R", "G"].indexOf(symb) >= 0)
				{mana = mana + '<img src="/static/symbols/' + symb + '.png" class="symbolimg-' + loc + '">' }
			else {mana = mana + '<img src="/static/symbols/gen' + symb + '.png" class="symbolimg-' + loc + '">'}
		}
		return mana
	}
	else { costs = cost.split(" // ");
		return [manaSpan(costs[0], loc), manaSpan(costs[1], loc)];
	}
} 

/*function cardString(cardname) {
	var arrows = '<span class="arrows"><a href="javascript:addToDeck(\'' +cardname.replace("'", "\\'") + '\')" class="addlink">▼</a><a href="javascript:pullFromDeck(\'' + cardname.replace("'", "\\'") + '\')" class="droplink">▲</a></span>'
	var manacost = manaSpan(getCost(cardname), 'vert');
	if (cardname.indexOf("//") == -1) {
		if (manacost.split(".png").length > 4) {var bufferspace = ' style="padding:0px 0px 0px 4px"';}
		else {var bufferspace = '';}
		return arrows + manacost + '</span><span class="cardname"' + bufferspace + '>' + cardname + '</span>'
	}
	else { cardnames = cardname.split(" // ");
		firstcost = manacost[0]
		secondcost = manacost[1]
		var bufferspace = ' style="padding:0px 0px 0px 0px"';
		return arrows + firstcost + '<span class="slashspan">//</span>' + secondcost + '</span><span class="cardname" style="padding:0px 0px 0px 4px">' + cardnames[0] + '</span><span class="slashspan">//</span><span class="cardname"' + bufferspace + '>' + cardnames[1] + '</span>'
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
/* }} */

function cardString(cardname, cost) {
	var arrows = '<span class="arrows"><a href="javascript:addToDeck(\'' +cardname.replace("'", "\\'") + '\')" class="addlink">▼</a><a href="javascript:pullFromDeck(\'' + cardname.replace("'", "\\'") + '\')" class="droplink">▲</a></span>'
	var manacost = manaSpan(cost, 'vert');
	if (cardname.indexOf("//") == -1) {
		if (manacost.split(".png").length > 4) {var bufferspace = ' style="padding:0px 0px 0px 4px"';}
		else {var bufferspace = '';}
		return arrows + manacost + '</span><span class="cardname"' + bufferspace + '>' + cardname + '</span>'
	}
	else { cardnames = cardname.split(" // ");
		firstcost = manacost[0]
		secondcost = manacost[1]
		var bufferspace = ' style="padding:0px 0px 0px 0px"';
		return arrows + firstcost + '<span class="slashspan">//</span>' + secondcost + '</span><span class="cardname" style="padding:0px 0px 0px 4px">' + cardnames[0] + '</span><span class="slashspan">//</span><span class="cardname"' + bufferspace + '>' + cardnames[1] + '</span>'
	}
}




function cmc(cardname) {
	var cost = getCost(cardname);
	if (cost == "nan") {return 1;}
	if (cardname.indexOf("//") != -1) { cost = cost.split(" // ")[0] ; }
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

function draftOrder(cardname, packno, pickno) {
	var pickdiv = document.getElementById("pick-" + packno + "-" + pickno) ;
	pickdiv.innerHTML = cardString(cardname) ;
}

function makePick(cardname, packno, pickno) {
	identifier = packno.toString() + "-" + pickno.toString()
	picked[identifier] = cardname;
	draftOrder(cardname, packno, pickno);
	}
	
//functions below have to do with moving the cards to and from the deck 
	
function addToDeck(cardname) {
	if (deck.indexOf(cardname) == -1) {
	deck.push(cardname) ; writeCMCs() ; }
}

function pullFromDeck(cardname) {
	var idx = deck.indexOf(cardname);
	deck.splice(idx, 1); writeCMCs() ;
}

function writeCard(cardname) { 
	var cardcmc = cmc(cardname);
	var creatureQ = isCreature(cardname) ;
	if (creatureQ) { var spanid = "creatures-" + cardcmc ; }
	else { var spanid = "noncreatures-" + cardcmc ; }
	var docspan = document.getElementById(spanid) ;
	var current = docspan.innerHTML;
	var present = '<div class="bottom-card">'
	var manacost = manaSpan(getCost(cardname), "bot")
	if (cardname.indexOf("//") != -1) {manacost = manacost[0]; }
	if (manacost.split(".png").length > 4) {
		var bufferspace = ' style="padding:0px 0px 0px 3px"';}
	else {var bufferspace = '';}
	present = present + manacost + '</span><span class="cardname-bot"' + bufferspace + '>' + cardname + '</span></div>'
	docspan.innerHTML = current + present ;
}

function writeCMCs() {
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