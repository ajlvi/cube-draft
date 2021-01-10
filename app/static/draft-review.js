function makePickBlock(p) {
	packno = 1 + Math.floor( p / (pickData["pack_size"] - pickData["tossed"]) );
	pickno = 1 + p % (pickData["pack_size"] - pickData["tossed"]);
	var ppstring = "p" + packno + "p" + pickno ;
	if ( pickData["packs"][p].length <= 8 )
		{
		var out = '<tr><td colspan=9 class="review-cell"><a id="' + ppstring + '"></a><div id="review-cell-' + ppstring + '"></div></td></tr><tr class="one-row-pack">';
		out = out + '<td class="pick-number-cell">Pack ' + packno.toString() + '<br>Pick ' + pickno.toString() + '<br><br><a href="#' + ppstring + '" class="review-permalink">link here</a><br><br><a href="javascript:showSnap(' + p.toString() + ')" class="review-permalink">toggle<br>pool</a></td>'
		for (pno = 0; pno < pickData["packs"][p].length; pno++) { 
			var cardID = pickData["packs"][p][pno]
			var cardimage = JSON.parse(pickData["seen_df"])["scryfall"][cardID]
			var wasPicked = false
			if ( pickData["picks"][p].indexOf(cardID) >= 0 ) { wasPicked = true }
			if ( wasPicked ) {
			out = out + '<td class="history-pick-cell"><div class="overtint"></div><img src="' +  cardimage + '" class="history-card-image"><div class="checkbox">&check;</div></td>';
				}
			else {
			out = out + '<td class="history-pick-cell"><img src="' + cardimage + '" class="history-card-image"></td>';
				}
			}
		var deficit = 8 - pickData["packs"][p].length
		if (deficit >= 1) { out = out + "<td colspan=" + deficit + "></td>" }
		out = out + "</tr>"; return out
		}
	else {
		var out = '<tr><td colspan=9 class="review-cell"><a id="' + ppstring + '"></a><div id="review-cell-' + ppstring + '"></div></td></tr><tr class="two-row-top">';
		out = out + '<td class="pick-number-cell">Pack ' + packno.toString() + '<br>Pick ' + pickno.toString() + '<br><br><a href="#' + ppstring + '" class="review-permalink">link here</a><br><br><a href="javascript:showSnap(' + p.toString() + ')" class="review-permalink">toggle<br>pool</a></td>'
		for (pno = 0; pno < 8; pno++) { 
			var cardID = pickData["packs"][p][pno]
			var cardimage = JSON.parse(pickData["seen_df"])["scryfall"][cardID]
			var wasPicked = false
			if ( pickData["picks"][p].indexOf(cardID) >= 0 ) { wasPicked = true }
			if ( wasPicked ) {
			out = out + '<td class="history-pick-cell"><div class="overtint"></div><img src="' + cardimage + '" class="history-card-image"><div class="checkbox">&check;</div></td>';
				}
			else {
			out = out + '<td class="history-pick-cell"><img src="' + cardimage + '" class="history-card-image"></td>';
				}
			}
		out = out + '</tr>\n<tr class="two-row-bot"><td></td>'
		for (pno = 8; pno < pickData["packs"][p].length; pno++) { 
			var cardID = pickData["packs"][p][pno]
			var cardimage = JSON.parse(pickData["seen_df"])["scryfall"][cardID]
			var wasPicked = false
			if ( pickData["picks"][p].indexOf(cardID) >= 0 ) { wasPicked = true }
			if ( wasPicked ) {
			out = out + '<td class="history-pick-cell"><div class="overtint"></div><img src="' + cardimage + '" class="history-card-image"><div class="checkbox">&check;</div></td>';
				}
			else {
			out = out + '<td class="history-pick-cell"><img src="' + cardimage + '" class="history-card-image"></td>';
				}
			}
		var deficit = 16 - pickData["packs"][p].length
		if (deficit >= 1) { out = out + "<td colspan=" + deficit + "></td>" }
		out = out + "</tr>"; return out
	}
}

function snapshotTable(p) {
	// first goal: read over the picks and determine everything's type and CMC
	var creat = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []} ;
	var noncreat = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []} ;
	cogworkID = findCogwork() //getting this out of the way up front
	var df = JSON.parse(pickData["seen_df"]) ;
	for (i = 0; i <= p; i ++) {
		packChoices = pickData["picks"][i] ; //could be length 1 or 2
		first_cmc = CMCcalc(df["cost"][packChoices[0]]) ;
		first_creat = df["creature"][packChoices[0]] ;
		if (first_creat == 1) { creat[first_cmc].push(packChoices[0]) ; }
		else { noncreat[first_cmc].push(packChoices[0]) ; }
		if (packChoices.length == 2) {
			creat[4] = creat[4].filter(function(e) { return e !== cogworkID }) ;
			second_cmc = CMCcalc(df["cost"][packChoices[1]]) ;
			second_creat = df["creature"][packChoices[1]] ;
			if (second_creat == 1) { creat[second_cmc].push(packChoices[1]) ; }
			else { noncreat[second_cmc].push(packChoices[1]) ; }
		}
	}
	// we now have all our picks sorted appropriately. it's time to build the table
	var draftTable = '<div class="draft-review-table">';
	for (cmc = 1; cmc <= 6; cmc++) {
		draftTable = draftTable + '<div class="draft-review-stack">'
		if (cmc == 1) { var cmcRep = '0-1'; } else { var cmcRep = cmc.toString() ; }
		draftTable = draftTable + '<span class="cost cmcbox">' + cmcRep + "</span>";
		draftTable = draftTable + '<span class="critter cmcbox">'
		for ( i = 0 ; i < creat[cmc].length; i++ ) { 
			draftTable = draftTable + cardDiv(creat[cmc][i]) ; }
		draftTable = draftTable + '</span><span class="spell cmcbox">'
		for ( i = 0 ; i < noncreat[cmc].length; i++) {
			draftTable = draftTable + cardDiv(noncreat[cmc][i]) ; }
		draftTable = draftTable + "</span></div>"
	}
	draftTable = draftTable + "</div>";
	return draftTable;	
}

function cardDiv(cardID) {
	var out = '<div class="review-card">'
	var cardcost = JSON.parse(pickData["seen_df"])["cost"][cardID]
	var cardname = JSON.parse(pickData["seen_df"])["card"][cardID]
	if (cardname == "Cogwork Librarian") { cardname = "<b>" + cardname + "</b>" }
	var manacost = manaSpan( cardcost, "bot" )
	if (cardcost.indexOf("//") >= 0) { manacost = manacost[0] }
	if (manacost.split(".png").length > 4) {
		var bufferspace = ' style="padding:0px 0px 0px 3px"';}
	else {var bufferspace = '';}
	out = out + manacost + '</span><span class="cardname-bot"' + bufferspace + '>' + cardname + '</span></div>'
	return out
}

function findCogwork() {
	var cogworkID = -1
	var df = JSON.parse(pickData["seen_df"])
	for (id in df["card"]) {
		if (df["card"][id] == "Cogwork Librarian") { cogworkID = id }
	}
	return cogworkID
}

function showSnap(p, ppstring) {
	packno = 1 + Math.floor( p / (pickData["pack_size"] - pickData["tossed"]) );
	pickno = 1 + p % (pickData["pack_size"] - pickData["tossed"]);
	var ppstring = "p" + packno + "p" + pickno ;
	if (ppstring == "p1p1") {return ;}
	var divname = "#review-cell-" + ppstring;
	var loc = $(divname)
	if (loc.html().length == 0) {loc.html(snapshotTable(p-1));}
	else {loc.html('') ;}
}
	
function tableString() {
	output = "<table id='history-table'>"
	for (i=0; i < Object.keys(pickData["picks"]).length; i++)
		{ output = output + "\n" + makePickBlock(i) }
	output = output + "</table>"
	return output
}

function makeTable() {
	loc = document.getElementById("table-loc")
	loc.innerHTML = tableString(); 
}

function CMCcalc(cost) {
	if (cost == null) {return 1;}
	if (cost.indexOf("//") != -1) { cost = cost.split(" // ")[0] ; }
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

function hashCheck(h) {
	var legal = ["#", "p", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"] ;
	for (i = 0; i < h.length; i++) {
		if (!legal.includes(h[i])) {return false;}
	}
	return true
}