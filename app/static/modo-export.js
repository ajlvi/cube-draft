function MODOExport(){
	cardpool = dataDump["chosen_cards"]
	outfile = '<?xml version="1.0" encoding="utf-8"?>'
	outfile = outfile + '\n<Deck xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
	outfile = outfile + '\n  <NetDeckID>0</NetDeckID>'
	outfile = outfile + '\n  <PreconstructedDeckID>0</PreconstructedDeckID>'
	for (drafted =0; drafted < cardpool.length; drafted++) {
		cube_id = cardpool[drafted]
		modo_id = JSON.parse(dataDump["chosen_df"])["mtgo"][cube_id]
		card_name = JSON.parse(dataDump["chosen_df"])["card"][cube_id].replace(" // ", "/")
		if (card_name == "Cogwork Librarian") { card_name = "Gilded Sentinel" }
		if (deck.length == 	0) { var sbloc = "false" }
		else if ( deck.includes(cube_id) ) { var sbloc = "false" }
		else { var sbloc = "true" }
		outfile = outfile + '\n  <Cards CatID="' + modo_id.toString() + '" Quantity="1" Sideboard="' + sbloc + '" Name="' + card_name + '" />'
	}
	outfile = outfile + '\n</Deck>'
	var d = new Date();
	var month = (1+d.getMonth()).toString().padStart(2, '0') ;
	var day = d.getDate().toString().padStart(2, '0') ;
	var year = (d.getYear()%100).toString()
	var date_string = year + "-" + month + "-" + day
	var filename = "cube-draft-" + dataDump["my_name"] + "-" + date_string + ".dek"
	download_file(outfile, filename, "text/csv")
}

/* this was stolen from https://stackoverflow.com/a/30832210 */
function download_file(data, filename, type) {
    var file = new Blob([data], {type: type});
    if (window.navigator.msSaveOrOpenBlob) // IE10+
        window.navigator.msSaveOrOpenBlob(file, filename);
    else { // Others
        var a = document.createElement("a"),
                url = URL.createObjectURL(file);
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        setTimeout(function() {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);  
        }, 0); 
    }
}