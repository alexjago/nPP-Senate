/* *** Predictor calculator. *** */

/* *** On page load: preload the base stats and calculate the splines. *** */

// Is there a way that works both locally and remotely?
// Yep, pre-process the CSV into a JS object - standard server-side compression
// Then include it in the page source, no dramas at all
// OK, so we have some JSON objects containing the preference breakdowns
//   for each district	

//console.log(district_prefs)

Array.prototype.max = function() {
  return Math.max.apply(null, this);
};

Array.prototype.min = function() {
  return Math.min.apply(null, this);
};


function Pct(num){
	return (num*100).toFixed(2) + "%";
}

var resultsTable;

$(document).ready(function(){
    resultsTable = $('#bigtable').DataTable({
    	/* No ordering applied by DataTables during initialisation */
        "order": [],
       	paging : false,
       	fixedHeader : true,
    });
});

var districts = {};

// Precalc 1: top-level 4PP on a per-district and statewide basis
// Also update the defaults in the UI for the statewide (yay reusability)


var pop_total = 0.0

var party_totals = {}
var party_totals_pct = {}

for(let party in district_prefs.parties){
	party_totals[party] = 0.0;
}

for (let distname in district_prefs.data) {
	//console.log(distname);
	
	var dist_firsts = {};
	var dist_total = district_prefs.data[distname][district_prefs.data[distname].length - 1];
	var dist_none = district_prefs.data[distname][0];
	var parties_subtotal = 0.0;
	
	pop_total += dist_total;
	
	for (let party in district_prefs.parties) {
		var dist_party = 0.0;
		for (i=0; i<district_prefs.field_names.length - 1; i++) {
			if (district_prefs.field_names[i].startsWith(party)) {
				dist_party += district_prefs.data[distname][i]
			}
		}
		parties_subtotal += dist_party;
		dist_firsts[party] = dist_party;
		party_totals[party] += dist_party;
	}
	dist_firsts["total"] = dist_total;
	
	for (let party in district_prefs.parties) {
		dist_firsts[party] += dist_none * dist_firsts[party] / parties_subtotal;
	}
	
	districts[distname] = dist_firsts
}

//console.log(districts);
//console.log(party_totals);
//console.log(pop_total);


// update party_pref defaults
// normalise these too
var p_sub_total = 0.0
for(let party in district_prefs.parties){
	p_sub_total += party_totals[party];
}
for(let party in district_prefs.parties){
	party_totals_pct[party] = (100 * party_totals[party] / p_sub_total).toFixed(2);
	$("#"+party+"StatewidePoll").val(party_totals_pct[party]);
}

// Precalc 2: get the splines for each party in each district

var splines = {}

for(let distname in district_prefs.data){
	
	splines[distname] = {}
	
	for(let partyname in district_prefs.parties){

		var x = party_totals_pct[partyname]/100.0	
		var y = districts[distname][partyname]/districts[distname]['total'];
		
		// createInterpolant(xs, ys)
		splines[distname][partyname] = createInterpolant([0.0, x, 1.0], [0.0, y, 1.0]);
	}
}

/* *** On clicking the "Calculate!" button, interpolate etc... *** */

// Now we know which party will be eliminated first. Eliminate and distribute.
// No doubt we will need to do some regex wackiness to figure out which columns
//  contain the relevant bits

var statewide = {}

var round_one = {}
var round_two = {}
var round_three = {}


var first_elims = {}
var second_elims = {}
var third_elims = {}
var winners = {}

$("#calculate").click(function(){

	// We should normalise "statewide" and update the inputs to reflect that
	var statewide_tot = 0.0
	// get values of things
	for(let partyname in district_prefs.parties){
		statewide[partyname] = Number($("#"+partyname+"StatewidePoll").val())/100.0;
		statewide_tot += statewide[partyname];
	}
	// Now normalise and update
	for(let partyname in district_prefs.parties){
		statewide[partyname] = statewide[partyname]/statewide_tot;
		$("#"+partyname+"StatewidePoll").val((100 * statewide[partyname]).toFixed(2));
	}

	// get first eliminated party.
	for (let distname in district_prefs.data){
		var _votes = [];
		var _parties = [];
		round_one[distname] = {};
		
		for(let partyname in district_prefs.parties){
			var pv = splines[distname][partyname](statewide[partyname]);
			round_one[distname][partyname] = pv;
			_votes.push(pv);
			_parties.push(partyname);
		}
		var least = _votes.indexOf(_votes.min());
		first_elims[distname] = [_parties[least], _votes[least]];
	}
	console.log("Round One:\n", round_one);
	console.log("First Eliminations:\n", first_elims);
	
	
	// Distribute 'second' preferences
	for (let distname in district_prefs.data){
		// what's the eliminated party?
		var elim = first_elims[distname][0];
		var nexts = {};
		var subtotal = 0.0;
		round_two[distname] = {}
		for (let party in district_prefs.parties) {
			if (party == elim) { 
				continue;
			}
			round_two[distname][party] = round_one[distname][party];
			var dist_party = 0.0;
			for (i=0; i<district_prefs.field_names.length - 1; i++) {
				if (district_prefs.field_names[i].startsWith(elim+party)) {
					dist_party += district_prefs.data[distname][i]
				}
			}
			nexts[party] = dist_party;
			subtotal += dist_party;
		}


		// Normalise next preferences & generate
		for (let party in nexts){
			round_two[distname][party] += 
				first_elims[distname][1] * nexts[party] / subtotal;
		}
	} 
	
	console.log("Round Two:\n", round_two);
	
	// get second eliminated party
	
	for(let distname in round_two){
		var _votes = [];
		var _parties = [];
		
		for(let partyname in round_two[distname]){
			_votes.push(round_two[distname][partyname])
			_parties.push(partyname)
		}
		
		var least = _votes.indexOf(_votes.min());
		second_elims[distname] = [_parties[least], _votes[least]];
	}
	console.log("Second Eliminations:\n", second_elims);
	
	// Distribute 'third' preferences

	for (let distname in round_two){
		// what's the eliminated party?
		var firstelim = first_elims[distname][0];
		var elim = second_elims[distname][0];
		var nexts = {};
		var subtotal = 0.0;
		round_three[distname] = {}
		for (let party in district_prefs.parties) {
			if (party == elim) { 
				continue;
			} else if (party == firstelim) {
				continue;
			}
			round_three[distname][party] = round_two[distname][party];
			var dist_party = 0.0;
			for (i=0; i<district_prefs.field_names.length - 1; i++) { 
				// if starts with Elim1, Elim2, me: distribute to me.
				// elif starts with Elim2, Elim1, me: distribute to me.
				// elif starts with Elim2, me: distribute to me.
				if(district_prefs.field_names[i].startsWith(firstelim+elim+party)){
					dist_party += district_prefs.data[distname][i];
				} else if (district_prefs.field_names[i].startsWith(elim+firstelim+party)){
					dist_party += district_prefs.data[distname][i];
				} else if (district_prefs.field_names[i].startsWith(elim+party)){
					dist_party += district_prefs.data[distname][i];
				} 

			}
			nexts[party] = dist_party;
			subtotal += dist_party;
		}

		// Normalise next preferences & generate
		for (let party in nexts){
			round_three[distname][party] += 
				second_elims[distname][1] * nexts[party] / subtotal;
		}
	} 

	console.log("Round Three:\n", round_three);

	// get third eliminated party and winner
	
	for(let distname in round_three){
		var _votes = [];
		var _parties = [];
		
		for(let partyname in round_three[distname]){
			_votes.push(round_three[distname][partyname])
			_parties.push(partyname)
		}
		
		var least = _votes.indexOf(_votes.min());
		third_elims[distname] = [_parties[least], _votes[least]];
		
		var most = _votes.indexOf(_votes.max());
		winners[distname] = [_parties[most], _votes[most]];
	}
	console.log("Runners-Up:\n", third_elims);
	console.log("Winners:\n", winners);


// Two-Party-Preferred:

// for each party, figure out which columns are for Labor and which are for LNP

let twoParties = ["Lab", "Lnp"];
var twoPartyCols = {};
var pattA = new RegExp("/"+twoParties[0]+"(?=.*"+twoParties[1]+")/");
var pattB = new RegExp("/"+twoParties[1]+"(?=.*"+twoParties[0]+")/");

for (let party in district_prefs.parties){
	
	twoPartyCols[party] = {};
	twoPartyCols[party][twoParties[0]] = [];
	twoPartyCols[party][twoParties[1]] = [];

	for (var i=0; i<district_prefs.field_names.length; i++) {
		fn = district_prefs.field_names[i]
		if(fn.startsWith(party)){ // quicksticks
			// if contains [0] and not [1], count for [0]
			if(fn.includes(twoParties[0]) & !fn.includes(twoParties[1])){
				twoPartyCols[party][twoParties[0]].push(i)
			// vice versa
			} else if(fn.includes(twoParties[1]) & !fn.includes(twoParties[0])){
				twoPartyCols[party][twoParties[1]].push(i)
			// if [0] occurs ahead of [1], count for [0]
			} else if (pattA.test(fn)){
				twoPartyCols[party][twoParties[0]].push(i)
			// vice versa
			} else if (pattB.test(fn)){
				twoPartyCols[party][twoParties[1]].push(i)
			}
		}
	}
}

console.log(twoPartyCols);

var distTPPs = {}; // this only needs to contain the score for [0]
// from `round_one` we have all the district-by-district primaries
// have to make the assumption of each sub-ordering inflated equally
// So need to calculate multiplicative factor

var totalTPP = 0.0

for (var dist in round_one) {
	distTPPs[dist] = 0.0

	for (party in district_prefs.parties) {
		var spline_multi = districts[dist]["total"] * round_one[dist][party] / (districts[dist][party]);
		
		// sum [0]
		var TPP_zero = 0.0
		for (col of twoPartyCols[party][twoParties[0]]){
			TPP_zero += district_prefs["data"][dist][col]
		}

		// sum [0]
		var TPP_one = 0.0
		for (col of twoPartyCols[party][twoParties[1]]){
			TPP_one += district_prefs["data"][dist][col]
		} 
		
		
		var TPP_multi = districts[dist][party]/(TPP_zero + TPP_one);
//		console.log(dist, party, TPP_multi, districts[dist][party], TPP_zero, TPP_one);

// then figure out 2PPs (display as Labor share in table)
		
		distTPPs[dist] += spline_multi * TPP_multi * TPP_zero
	}
	
	totalTPP += distTPPs[dist]
}


/* *** ... and finally send it to DataTables to update. *** */

// Columns: District Name, Greens 4PP, Labor 4PP, Liberal National 4PP, One Nation 4PP,
// ... 1st elimination, Greens 3PP, Labor 3PP, Liberal National 3PP, One Nation 3PP,
// ... 2nd elimination, Greens 2PP, Labor 2PP, Liberal National 2PP, One Nation 2PP, 
// ... Runner-up, Winner, 2PP (Labor)

// (the above defined in HTML)

var bigtable = [];

var parties = ["Grn", "Lab", "Lnp", "Phn"];
var columns = ["District Name", "Greens 4PP", "Labor 4PP", "Liberal National 4PP", "One Nation 4PP", 
		"1st elim.", "Greens 3PP", "Labor 3PP", "Liberal National 3PP", "One Nation 3PP",
		"2nd elim.", "Greens 2PP", "Labor 2PP", "Liberal National 2PP", "One Nation 2PP", 
		"Runner-up", "Winner", "2PP (Labor)"]

colsitemd = [];

for(i=0; i<columns.length; i++){
	colsitemd.push({"title" : columns[i]});
}

for (let distname in district_prefs.data){
	var row = []
	row.push(distname);
	
	for (i=0; i<4; i++){
		party = parties[i];
		row.push(Pct(round_one[distname][party]));
	}
	
	row.push(district_prefs.parties[first_elims[distname][0]]);
	
	for (i=0; i<4; i++){
		party = parties[i];
		// need to insert "NA1" if null
		if(first_elims[distname][0] == party){
			row.push(" NA1"); // the space is so it'll sort as < 0.00
		} else {
			row.push(Pct(round_two[distname][party]));
		}
	}

	row.push(district_prefs.parties[second_elims[distname][0]]);
	
	for (i=0; i<4; i++){
		party = parties[i];
		// need to insert "NA1" if null
		if(party == first_elims[distname][0]){
			row.push(" NA1"); // the space is so it'll sort as < 0.00
		} else if(party == second_elims[distname][0]){
			row.push(" NA2"); // the space is so it'll sort as < 0.00
		} else {
			row.push(Pct(round_three[distname][party]));
		}
	}
	
	row.push(district_prefs.parties[third_elims[distname][0]]);
	row.push(district_prefs.parties[winners[distname][0]]);
	
	row.push(Pct(distTPPs[distname]/districts[distname]["total"]));
	
	var rowitem = {}
	
	for(i=0; i<columns.length; i++){
		rowitem[columns[i]] = row[i];
	}
	
	bigtable.push(row);
		
}

console.log("Results:\n", bigtable);

resultsTable = $("#bigtable").DataTable({
	data : bigtable,
	columns : colsitemd,
	destroy : true,
	paging : false,
	fixedHeader : true,
	columnDefs : [ 
		{targets : "_all", width : "1em"},
		{targets : [1,2,3,4,6,7,8,9,11,12,13,14,17], className : "dt-body-right"}
	]
});

// Update seat tally:

for(var party of parties){
	var winnerCounts = 0;
	for(var distname in winners){
		if(winners[distname][0] == party){
			winnerCounts++;
		}
	}
	$("#"+party+"Seats").html("<p>"+winnerCounts.toString()+"</p>");
} 

// Update global TPP

$("#"+twoParties[0]+"2PP").html("<p>"+Pct(totalTPP/pop_total)+"</p>");
$("#"+twoParties[1]+"2PP").html("<p>"+Pct(1 - totalTPP/pop_total)+"</p>");

});

