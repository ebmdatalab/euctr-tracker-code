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
	    { "width": "23%", "orderSequence": [ "asc", "desc" ] },
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

    /* Chart */
    var ctx = document.getElementById("overview_chart");

    Chart.defaults.global.defaultFontFamily = "Georgia, 'Times New Roman', Times, serif"
    Chart.defaults.global.defaultFontSize = 15
    Chart.defaults.global.defaultFontColor = '#333'

    var data = {
	labels: [
	    "Number of trials"
	],
	datasets: [
	{
	    label: "Due - Reported",
	    data: [total_due - total_unreported],
	    backgroundColor: [ "#22B24C" ],
	    hoverBackgroundColor: [ "#22B24C" ]
       	},
	{
	    label: "Due - Not reported",
	    data: [total_unreported],
	    backgroundColor: [ "#EB6864" ],
	    hoverBackgroundColor: [ "#EB6864" ]
        },
	{
	    label: "Not due",
	    data: [not_yet_due_trials],
	    backgroundColor: [ "#999" ],
	    hoverBackgroundColor: [ "#999" ]
        },
	{
	    label: "Bad data",
	    data: [inconsistent_trials],
	    backgroundColor: [ "#7632B0" ],
	    hoverBackgroundColor: [ "#7632B0" ]
        },
	]
    };

    var options = {
        animation:{
            animateScale: true
        },
	scales: {
	    xAxes: [{
		stacked: true,
		display: false
	    }],
	    yAxes: [{
		stacked: true,
		display: false
	    }]
	},
	onResize: function() {
	    // Hide legend on small browser widths, otherwise
            // chart itself disappears.
	    var height = $('#overview_chart').height()
	    if (height < 150) {
		window.chart.options.legend.display = false
	    } else {
		window.chart.options.legend.display = true
            }
	},
	legend: {
	    display: true
	},
	title: {
	    display: true,
	    text: 'Out of ' + total_trials + ' trials on the registry'
	}
    }

    window.chart = new Chart(ctx,{
	type: 'horizontalBar',
	data: data,
	options: options
    });

    ctx.onclick = function(evt) {
	var pt = window.chart.getDatasetAtEvent(evt)
	legendItem = pt[0]['_datasetIndex']
	if (legendItem == 0 || legendItem == 1) {
	    show_due()
	} else if (legendItem == 2) {
	    show_not_yet_due()
	} else if (legendItem == 3) {
	    show_bad_data()
	}
    }
}


