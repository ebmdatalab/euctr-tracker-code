function hide_sponsor_datatable() {
    /* Hide while loading to prevent style change jitter */
    $('#sponsor_table').hide()
    $('#sponsor_table_loading').show()
    $('#sponsor-pills').hide()
}

function activate_sponsor_datatable() {
    var t = $('#sponsor_table').DataTable({
        "order": [[ 4, "desc" ]],
	"paging": false,
	"aoColumns": [
	    { "orderSequence": [ "asc", "desc" ] },
	    { "orderSequence": [ "desc", "asc" ], "className": "dt-right" },
	    { "orderSequence": [ "desc", "asc" ], "className": "dt-right"  },
	    { "orderSequence": [ "desc", "asc" ], "className": "dt-right"  },
	    { "orderSequence": [ "desc", "asc" ], "className": "dt-right"  },
	    { "orderSequence": [ "asc", "desc" ] }, // Hidden column
	]
    });

    var show_all = function() {
	t.search("")
	t.columns(5).search("").draw()
	$('#all_sponsors').addClass('active')
	$('#major_sponsors').removeClass('active')
	return false
    }
    $('#all_sponsors').on('click', show_all)
    var show_major = function() {
	t.search("")
	t.columns(5).search("major").draw()
	$('#major_sponsors').addClass('active')
	$('#all_sponsors').removeClass('active')
	return false
    }
    $('#major_sponsors').on('click', show_major)
    show_major();

    t.on('search.dt', function () {
	var major_search = t.columns(5).search().join()
	if (t.search() == "") {
	    if (major_search == "major") {
		$('#major_sponsors').addClass('active')
		$('#all_sponsors').removeClass('active')
	    } else {
		$('#all_sponsors').addClass('active')
		$('#major_sponsors').removeClass('active')
	    }
	} else {
	    if (major_search == "major") {
		t.columns(5).search("")
	    }
	    $('#all_sponsors').removeClass('active')
	    $('#major_sponsors').removeClass('active')
	}
    })

    /* Show after style change */
    $('#sponsor_table_loading').hide()
    $('#sponsor-pills').show()
    $('#sponsor_table').show()
}

$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})

function hide_trials_datatable() {
    /* Hide while loading to prevent style change jitter */
    $('#trials_table').hide()
    $('#trials_table_loading').show()
}

function activate_trials_datatable() {
    var t = $('#trials_table').DataTable({
/*        "order": [[ 4, "desc" ]], */
	"paging": false
/*	"aoColumns": [
	    { "orderSequence": [ "asc", "desc" ] },
	    { "orderSequence": [ "desc", "asc" ], "className": "dt-right" },
	    { "orderSequence": [ "desc", "asc" ], "className": "dt-right"  },
	    { "orderSequence": [ "desc", "asc" ], "className": "dt-right"  },
	    { "orderSequence": [ "desc", "asc" ], "className": "dt-right"  },
	    { "orderSequence": [ "asc", "desc" ] }, // Hidden column
	]
*/
    });
    /* Show after style change */
    $('#trials_table_loading').hide()
    $('#trials_table').show()
}


