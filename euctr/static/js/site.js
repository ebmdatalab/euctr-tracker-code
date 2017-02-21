$(document).ready( function () {
    var t = $('#table4_table').DataTable({
        "order": [[ 4, "desc" ]],
        //order": [[ 3, "desc" ], [2, "desc"], [0, "asc"]], // reproduce order in paper
	"paging": false,
	"aoColumns": [
	    { "orderSequence": [ "asc", "desc" ] },
	    { "orderSequence": [ "desc", "asc" ], "className": "dt-right" },
	    { "orderSequence": [ "desc", "asc" ], "className": "dt-right"  },
	    { "orderSequence": [ "desc", "asc" ], "className": "dt-right"  },
	    { "orderSequence": [ "desc", "asc" ], "className": "dt-right"  }
	]
    });
} );
