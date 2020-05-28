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