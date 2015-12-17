/**

 * This javascript file checks for the brower/browser tab action.

 * It is based on the file menstioned by Daniel Melo.

 * Reference: http://stackoverflow.com/questions/1921941/close-kill-the-session-when-the-browser-or-tab-is-closed

 */

var validNavigation = false;

function endSession() {
	// Browser or broswer tab is closed
	// Do sth here ...
}

function wireUpEvents() {
/*
* For a list of events that triggers onbeforeunload on IE
* check http://msdn.microsoft.com/en-us/library/ms536907(VS.85).aspx
*/
	window.onbeforeunload = function() {
		if (!validNavigation) {
			function delCookie(name,path,domain) {
			var today = new Date();
			var deleteDate = new Date(today.getTime() - 48 * 60 * 60 * 1000); // minus 2 days
			var cookie = name + "="
                     + ((path == null) ? "" : "; path=" + path)
                     + ((domain == null) ? "" : "; domain=" + domain)
                     + "; expires=" + deleteDate;
            document.cookie = cookie;
		}
 
         function delOblixCookie() {
            // set focus to ok button
            var isNetscape = (document.layers);
            if (isNetscape == false || navigator.appVersion.charAt(0) >= 5) {
            for (var i=0; i<document.links.length; i++) {
                  if (document.links[i].href == "javascript:top.close()") {
                  document.links[i].focus();
                  break;
                  }
                }
             }
             delCookie('ObTEMC', '/');
             delCookie('ObSSOCookie', '/');
 
             // Added myCustomAppCookie deletion
             delCookie('myCustomApp', '/');
 
             // in case cookieDomain is configured
             // delete same cookie from all subdomains
                   var subdomain;
                   var domain = new String(document.domain);
                   var index = domain.indexOf(".");
                   while (index > 0) {
                          subdomain = domain.substring(index, domain.length);
                          if (subdomain.indexOf(".", 1) > 0) {
                                 delCookie('ObTEMC', '/', subdomain);
                                 delCookie('ObSSOCookie', '/', subdomain);
                          }
                          domain = subdomain;
                          index = domain.indexOf(".", 1);
                    }
                 }
      }

  }

 // Attach the event keypress to exclude the F5 refresh
	$('html').bind('keypress', function(e) {
		if (e.keyCode == 116){
			validNavigation = true;
		}
	});
// Attach the event click for all links in the page
	$("a").bind("click", function() {
	validNavigation = true;
	});
// Attach the event submit for all forms in the page
	$("form").bind("submit", function() {
		validNavigation = true;
	});
// Attach the event click for all inputs in the page
$("input[type=submit]").bind("click", function() {
	validNavigation = true;
	});
}
// Wire up the events as soon as the DOM tree is ready

$(document).ready(function() {
	wireUpEvents(); 
});