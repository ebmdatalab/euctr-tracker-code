/* Hide while loading to prevent style change jitter */
function hide_datatable() {
    $('#sponsor_table').hide()
}

function activate_datatable() {
    var t = $('#sponsor_table').DataTable({
        "order": [[ 4, "desc" ]],
	"paging": false,
	"aoColumns": [
	    { "orderSequence": [ "asc", "desc" ] },
	    { "orderSequence": [ "desc", "asc" ], "className": "dt-right" },
	    { "orderSequence": [ "desc", "asc" ], "className": "dt-right"  },
	    { "orderSequence": [ "desc", "asc" ], "className": "dt-right"  },
	    { "orderSequence": [ "desc", "asc" ], "className": "dt-right"  }
	]
    });
    /* Show after style change */
    $('#sponsor_table').show()
}
