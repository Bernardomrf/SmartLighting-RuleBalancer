var evtSrc = new EventSource("/subscribe");
var eventOutputContainer = document.getElementById("event");
evtSrc.onmessage = function(e) {
	json = JSON.parse(e.data);
	//console.log(json);
	//console.log(json['rules'][0])
	text ="";
	for (var val in json['gateways']) {

		//console.log(val);
		text += "<p><span>Gateway " + val + " - " +json['gateways'][val] + " devices</span></p>";

	}
	for (var val in json['rules']) {

		//console.log(val);
		text += "<p><span>Rule " + val + " - " +json['rules'][val] + "</span></p>";

	}
	eventOutputContainer.innerHTML = text;

};
