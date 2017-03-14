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

const DEFAULT_SPONSOR_ORDER = 3
const DEFAULT_SPONSOR_ORDER_DIR = "desc"
const MAJOR_SPONSOR_COLUMN = 5

const DEFAULT_TRIAL_ORDER = 1
const DEFAULT_TRIAL_ORDER_DIR = "desc"
const DUE_TRIAL_COLUMN=4

function activate_sponsor_datatable() {
    var t = $('#sponsor_table').DataTable({
	"fixedHeader": true,
        "order": [[ DEFAULT_SPONSOR_ORDER, DEFAULT_SPONSOR_ORDER_DIR ]],
	"pageLength": 100,
	"lengthMenu": [ [10, 100, 500, -1], [10, 100, 500, "All"] ],
	"orderClasses": false, // Turns off column highlighting, so sorting much faster
	"dom": "tlpr",
	"autoWidth": false,
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
        "order": [[ DEFAULT_TRIAL_ORDER, DEFAULT_TRIAL_ORDER_DIR ]],
	"pageLength": 100,
	"lengthMenu": [ [10, 100, 500, -1], [10, 100, 500, "All"] ],
	"orderClasses": false, // Turns off column highlighting, so sorting much faster
	"dom": "tlpr",
	"autoWidth": false,
	"aoColumns": [
	    { "orderData": [0,1], "width": "23%", "orderSequence": [ "asc", "desc" ] },
	    { "width": "15%", "orderSequence": [ "asc", "desc" ] },
	    { "width": "45%", "orderSequence": [ "asc", "desc" ] },
	    { "width": "17%", "orderSequence": [ "desc", "asc" ], "className": "dt-right" },
	    { "width": "0%", "orderSequence": [ "asc", "desc" ] }, // Hidden column
	]
    });
    $('#trials_table').on('draw.dt', function() {
	$('#trials_table [data-toggle="tooltip"]').tooltip()
    })

    var show_due = function() {
	t.search("")
	t.columns(DUE_TRIAL_COLUMN).search("due-trials").draw()
	$('li.active').removeClass('active')
	$('#due_trials').addClass('active')
	$('.trials_preamble > *').hide()
	$('.due_trials_preamble').show()
	return false
    }
    var show_not_yet_due = function() {
	t.search("")
	t.columns(DUE_TRIAL_COLUMN).search("not-yet-due").draw()
	$('li.active').removeClass('active')
	$('#not_yet_due_trials').addClass('active')
	$('.trials_preamble > *').hide()
	$('.not_yet_due_preamble').show()
	return false
    }
    var show_bad_data = function() {
	t.search("")
	t.columns(DUE_TRIAL_COLUMN).search("bad-data").draw()
	$('li.active').removeClass('active')
	$('#bad_data_trials').addClass('active')
	$('.trials_preamble > *').hide()
	$('.bad_data_preamble').show()
	return false
    }
     var show_search = function() {
	var search = $('#search_trials input').val()
	t.search(search)
	t.columns(DUE_TRIAL_COLUMN).search("").draw()
	var count = t.page.info().recordsDisplay
	if (count < 16) {
	    // Prevent jumping in scrolling as values are filtered
	    $('footer').css("margin-bottom", "420px")
	} else {
	    $('footer').css("margin-bottom", "0px")
	}
	t.draw(false)
	$('#search_trials .badge').text(count)

	$('li.active').removeClass('active')
	$('#search_trials').addClass('active')
	$('.trials_preamble > *').hide()
	return false
    }
 
    $('#due_trials').on('click', show_due)
    $('#not_yet_due_trials').on('click', show_not_yet_due)
    $('#bad_data_trials').on('click', show_bad_data)
    $('#search_trials input').on('input', show_search)
    $('#search_trials').on('click', show_search)
    $('#search_trials button').on('submit', show_search)
    show_due()

    /* Show after style change */
    $('#trials_table_loading').hide()
    $('#trials_table').show()

    /* Charts */
    Chart.defaults.global.defaultFontFamily = "Georgia, 'Times New Roman', Times, serif"
    Chart.defaults.global.defaultFontSize = 15
    Chart.defaults.global.defaultFontColor = '#333'

    var unreported_data = {
	labels: [ "Reported on time", "Late reporting results" ],
	datasets: [
	{
	    data: [total_due - total_unreported, total_unreported],
	    backgroundColor: [ "#999", "#EB6864" ],
	    hoverBackgroundColor: [ "#999", "#EB6864" ]
       	},
	]
    };
    var overview_data = {
	labels: [ "Good data", "Bad data" ],
	datasets: [
	{
	    data: [total_due + not_yet_due_trials, inconsistent_trials],
	    backgroundColor: [ "#999", "#B264B2" ],
	    hoverBackgroundColor: [ "#999", "#B264B2" ]
       	},
	]
    };

    var options = {
	legend: { display: false },
    }

    var overview_ctx = document.getElementById("overview_chart");
    window.overview_chart = new Chart(overview_ctx, {
	type: 'pie' ,
	data: overview_data,
	options: options
    });

    var unreported_ctx = document.getElementById("unreported_chart");
    window.unreported_chart = new Chart(unreported_ctx, {
	type: 'pie' ,
	data: unreported_data,
	options: options
    });

}

