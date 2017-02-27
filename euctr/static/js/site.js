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
}
