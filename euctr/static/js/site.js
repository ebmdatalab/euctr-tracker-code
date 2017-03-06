/****************************************************************/
/* General */

$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})


/****************************************************************/
/* Front page */

function hide_sponsor_datatable() {
    /* Hide while loading to prevent style change jitter */
    $('#sponsor_table').hide()
    $('#sponsor_table_loading').show()
    $('#table-pills').hide()
}

function activate_sponsor_datatable() {
    var t = $('#sponsor_table').DataTable({
	"fixedHeader": true,
        "order": [[ 4, "desc" ]],
	"pageLength": 100,
	"lengthMenu": [ [10, 100, 500, -1], [10, 100, 500, "All"] ],
	"orderClasses": false, // Turns off column highlighting, so sorting much faster
	"dom": "tlpr",
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
	$('#search_sponsors').removeClass('active')
	return false
    }
    var show_major = function() {
	t.search("")
	t.columns(5).search("major").draw()
	$('#major_sponsors').addClass('active')
	$('#all_sponsors').removeClass('active')
	$('#search_sponsors').removeClass('active')
	return false
    }
    var show_search = function() {
	var search = $('#search_sponsors input').val()
	t.search(search)
	t.columns(5).search("")
	var count = t.page.info().recordsDisplay
	if (count < 16) {
	    // Prevent jumping in scrolling as values are filtered
	    $('footer').css("margin-bottom", "420px")
	} else {
	    $('footer').css("margin-bottom", "0px")
	}
	t.draw(false)
	$('#major_sponsors').removeClass('active')
	$('#all_sponsors').removeClass('active')
	$('#search_sponsors').addClass('active')
	$('#search_sponsors .badge').text(count)
	return false
    }
    $('#all_sponsors').on('click', show_all)
    $('#major_sponsors').on('click', show_major)
    $('#search_sponsors input').on('input', show_search)
    $('#search_sponsors').on('click', show_search)
    $('#search_sponsors button').on('submit', show_search)
    show_major();

    /* Show after style change */
    $('#sponsor_table_loading').hide()
    $('#table-pills').show()
    $('#sponsor_table').show()
    $('#sponsor_table').show()
    t.draw()
}


/****************************************************************/
/* Sponsor page */

function hide_trials_datatable() {
    /* Hide while loading to prevent style change jitter */
    $('#trials_table').hide()
    $('#trials_table_loading').show()
}

function activate_trials_datatable() {
    var t = $('#trials_table').DataTable({
	"fixedHeader": true,
        "order": [[ 3, "desc" ]],
	"pageLength": 100,
	"lengthMenu": [ [10, 100, 500, -1], [10, 100, 500, "All"] ],
	"orderClasses": false, // Turns off column highlighting, so sorting much faster
	"dom": "tlpr",
	"aoColumns": [
	    { "orderSequence": [ "asc", "desc" ] },
	    { "orderSequence": [ "asc", "desc" ] },
	    { "orderSequence": [ "asc", "desc" ] },
	    { "orderSequence": [ "desc", "asc" ], "className": "dt-right" },
	    { "orderSequence": [ "desc", "asc" ], "className": "dt-right" },
	]
    });
    /* Show after style change */
    $('#trials_table_loading').hide()
    $('#trials_table').show()
}


