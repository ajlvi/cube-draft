function vertBar(packs, picks) {
	var outstring = '<div class="draft-picks">' ;
	for (p=1; p <= packs; p++) {
		for (k=1; k <= picks; k++) {
			outstring += '\n<div class="pick" id="pick-' + p + '-' + k + '"><span class="unpicked">'+ k + '</span></div>';
		}
		if (p != packs) {outstring += '\n<hr class="divider">\n\n';}
	}
	outstring += "\n</div>" ;
	vertContainer = document.getElementById('vertbar');
	vertContainer.innerHTML = outstring;
	vertbardone = true;
}

function flowBar(input=1) {
	//input is only checked to see if it's zero, in which case do nothing
	if (input == 0) { $('#flow-info').html(''); return }
	drafters = dataDump.drafters
	if (dataDump.packno % 2 == 0) { var arrow = "&#x27f6;" }
	else { var arrow = "&#x27f5;" }
	arrowbox = "<span class='arrow'>" + arrow + "</span>"
	output = arrowbox;
	for (pers = 0 ; pers < drafters.length; pers++) {
		if (dataDump.packno == 0) { var spanclass = "drafter-box unstarted" ; }
		else { var spanclass = "drafter-box" ; }
		output = output + "<span class='" + spanclass + "'>" + drafters[pers] + "</span>" + arrowbox ;
	}
	$('#flow-info').html(output) ;
}