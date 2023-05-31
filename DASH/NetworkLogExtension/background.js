var contentport;

chrome.runtime.onConnect.addListener(function(port) {
  console.assert(port.name == "netlogextension");
  contentport = port;
});

function logFunc(requestDetails, tag) {
  var date = new Date();
  logstr = tag + " " + date.getTime() + " " + JSON.stringify(requestDetails);
	contentport.postMessage(logstr);
}

chrome.webRequest.onBeforeRequest.addListener(
  function(x){logFunc(x,"BEFORE_REQUEST")},
  {urls: ["<all_urls>"]}
);

// long on first byte received
chrome.webRequest.onResponseStarted.addListener(
  function(x){logFunc(x,"RESPONSE_STARTED")},
  {urls: ["<all_urls>"]}
);

// long on header
chrome.webRequest.onSendHeaders.addListener(
  function(x){logFunc(x,"SEND_HEADERS")},
  {urls: ["<all_urls>"]}
);

// log response finished
chrome.webRequest.onCompleted.addListener(
  function(x){logFunc(x,"COMPLETE")},
  {urls: ["<all_urls>"]},
  ["responseHeaders"]
);
