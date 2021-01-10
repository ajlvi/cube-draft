$(document).ready(function(){
	var filepicker = document.getElementById("upload-input");
	filepicker.onchange = function() {
		verifyDek() ;
	}
});

function verifyDek() {
	var up = document.getElementById("upload-input")
	fname = up.files[0].name;
	if (fname.slice(fname.length -4, fname.length) == ".dek")
		{var outmsg = ".dek file uploaded"}
	else {
		var outmsg = "choose a .dek file";
		up.value = '';
	}
	var outslot = document.getElementById("uploaded-filename")
	outslot.innerHTML = outmsg; 
}

function dekFileLines() {
	var upp = document.getElementById("upload-input"); 
	var dekfile = upp.files[0];
	var freader = new FileReader();
	freader.readAsText(dekfile);
	freader.onload = function(e) {
		var lines = freader.result.split("\n");
		return lines }
	return lines
}