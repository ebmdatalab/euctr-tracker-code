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

const DEFAULT_SPONSOR_ORDER = 4
const DEFAULT_SPONSOR_ORDER_DIR = "desc"
const MAJOR_SPONSOR_COLUMN = 5

function activate_sponsor_datatable() {
    var t = $('#sponsor_table').DataTable({
	"fixedHeader": true,
        "order": [[ DEFAULT_SPONSOR_ORDER, DEFAULT_SPONSOR_ORDER_DIR ]],
	"pageLength": 100,
	"lengthMenu": [ [10, 100, 500, -1], [10, 100, 500, "All"] ],
	"orderClasses": false, // Turns off column highlighting, so sorting much faster
	"dom": "tlpr",
	"autoWidth": true,
	"aoColumns": [
	    { "width": "30%", "orderSequence": [ "asc", "desc" ] },
	    { "width": "17.5%", "orderSequence": [ "desc", "asc" ], "className": "dt-right" },
	    { "width": "17.5%", "orderSequence": [ "desc", "asc" ], "className": "dt-right"  },
	    { "width": "17.5%", "orderSequence": [ "desc", "asc" ], "className": "dt-right"  },
	    { "width": "17.5%", "orderSequence": [ "desc", "asc" ], "className": "dt-right"  },
	    { "width": "0%", "orderSequence": [ "asc", "desc" ] }, // Hidden column
	],
    });

    var show_all = function() {
	t.search("")
	t.columns(MAJOR_SPONSOR_COLUMN).search("").draw()
	$('#all_sponsors').addClass('active')
	$('#major_sponsors').removeClass('active')
	$('#search_sponsors').removeClass('active')
	return false
    }
    var show_major = function() {
	t.search("")
	t.columns(MAJOR_SPONSOR_COLUMN).search("major").draw()
	$('#major_sponsors').addClass('active')
	$('#all_sponsors').removeClass('active')
	$('#search_sponsors').removeClass('active')
	return false
    }
    var show_search = function() {
	var search = $('#search_sponsors input').val()
	t.search(search)
	t.columns(MAJOR_SPONSOR_COLUMN).search("")
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

    // t.on('column-sizing.dt', function() { alert('column-sizing') })

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
        "order": [[ 1, "asc" ]],
	"pageLength": 100,
	"lengthMenu": [ [10, 100, 500, -1], [10, 100, 500, "All"] ],
	"orderClasses": false, // Turns off column highlighting, so sorting much faster
	"dom": "tlpr",
	"autoWidth": true,
	"aoColumns": [
	    { "width": "15%", "orderSequence": [ "asc", "desc" ] },
	    { "width": "15%", "orderSequence": [ "asc", "desc" ] },
	    { "width": "55%", "orderSequence": [ "asc", "desc" ] },
	    { "width": "15%", "orderSequence": [ "desc", "asc" ], "className": "dt-right" },
	]
    });
    $('#trials_table').on('draw.dt', function() {
	$('#trials_table [data-toggle="tooltip"]').tooltip()
    })

    var show_search = function() {
	var search = $('#search_trials input').val()
	t.search(search)
	var count = t.page.info().recordsDisplay
	if (count < 16) {
	    // Prevent jumping in scrolling as values are filtered
	    $('footer').css("margin-bottom", "420px")
	} else {
	    $('footer').css("margin-bottom", "0px")
	}
	t.draw(false)
	$('#search_trials .badge').text(count)
	return false
    }
 
    $('#search_trials input').on('input', show_search)
    $('#search_trials').on('click', show_search)
    $('#search_trials button').on('submit', show_search)

    /* Show after style change */
    $('#trials_table_loading').hide()
    $('#trials_table').show()
}


