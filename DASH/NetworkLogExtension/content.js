console.log("CONTENT SCRIPT");

var port = chrome.runtime.connect({name: "netlogextension"});
var video_duration = null;
var counter = 0;
var timer = 0;

function get_video_duration() {
	return video_duration;
}

function set_video_duration(vdur) {
	video_duration = vdur;
}

function get_counter() {
	return counter;
}

function set_counter(val) {
	counter = val;
}

var check = setInterval(() => {
	timer += 1;
	var c = get_counter();
	if (timer > 120 && c < 2) {
		console.log("Closing window", 0);
		window.close();
	}
}, 1000)


port.onMessage.addListener(function(msg, requestDetails) {
	console.log(msg);

	var c = get_counter();
	if (msg.indexOf("videoplayback") > -1) {
		set_counter(c + 1);
	}

	if (get_video_duration() === null && msg.indexOf("videoplayback") > 0) {
		let dur_index = msg.indexOf("&dur=");
		if (dur_index > 0) {
			let end_index = msg.indexOf("&", dur_index+1);

			if (end_index == -1)
				end_index = msg.indexOf('"', dur_index+1);

			let dur_value = msg.slice(dur_index + 5, end_index);
			video_duration = Number(dur_value)
		}
		set_video_duration(video_duration)
	}

	if (msg.indexOf("streamingstats") > 0) {
		if (msg.indexOf("COMPLETE") > -1) {
			let bh_index = msg.indexOf("&bh=")
			if (bh_index > 0) {
				let end_index = msg.indexOf("&", bh_index+1)
				if (end_index == -1)
					end_index = msg.indexOf('"', bh_index+1)
				let bh_values = (msg.slice(bh_index + 4, end_index)).split(",")
				let buffer = bh_values[bh_values.length-1].split(":")[1]

				if (buffer >= 1000) {
					console.log("Closing window", buffer)
					window.close();
				}
			}
		}
	}
});