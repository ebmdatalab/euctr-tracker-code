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

const DEFAULT_SPONSOR_ORDER = 2
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
	    { "width": "17.5%", "orderSequence": [ "desc", "asc" ], "className": "dt-right", "type": "num-fmt" },
	    { "width": "17.5%", "orderSequence": [ "desc", "asc" ], "className": "dt-right"  },
	    { "width": "0%", "orderSequence": [ "asc", "desc" ] }, // Hidden column
	],
    });

    /* The three tabs - major, all and search - can be flipped between
     * at will. So the front page loads fast (necessary for e.g. Twitter cards)
     * only partial list of sponsors is loaded for "major". First time going 
     * to "all" or "search" a whole new page is loaded. After that, it is
     * all done with Javascript so is instant.
     *
     * There is use of window.history to make sure the back button behaves
     * consistently with these two ways of reaching the same page.
     */
    var show_all = function(ev) {
	t.search("")
	t.columns(MAJOR_SPONSOR_COLUMN).search("").draw()
	$('#all_sponsors').addClass('active')
	$('#major_sponsors').removeClass('active')
	$('#search_sponsors').removeClass('active')
	if (ev) {
	    window.history.pushState('all', '', '/?all');
	}
	return false
    }
    var show_major = function(ev) {
	t.search("")
	t.columns(MAJOR_SPONSOR_COLUMN).search("major").draw()
	$('#major_sponsors').addClass('active')
	$('#all_sponsors').removeClass('active')
	$('#search_sponsors').removeClass('active')
	if (ev) {
	    window.history.pushState('major', '', '/');
	}
	return false
    }
    var show_search = function(ev) {
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
	if (ev) {
	    window.history.pushState('search', '', '/?search');
	}
	return false
    }
    var redirect_search = function() {
	$('#search_sponsors input').blur() 
	$(location).attr('href', '/?search') 
    }
    if (showing_all_sponsors) {
	$('#all_sponsors').on('click', show_all)
    }
    $('#major_sponsors').on('click', show_major)
    if (showing_all_sponsors) {
	$('#search_sponsors input').on('input', show_search)
	$('#search_sponsors').on('click', show_search)
	$('#search_sponsors button').on('submit', show_search)
    } else {
	$('#search_sponsors input').on('input', redirect_search)
	$('#search_sponsors').on('click', redirect_search)
	$('#search_sponsors button').on('submit', redirect_search)
    }
    function initial_tab() {
	if (activate_search) {
	    show_search(null)
	    $('#search_sponsors input').focus()
	} else if (showing_all_sponsors) {
	    show_all(null);
	} else {
	    show_major(null);
	}
    }
    initial_tab()

    window.onpopstate = function(ev) {
	if (ev.state == "search") {
	    show_search(null)
	} else if (ev.state == "all") {
	    show_all(null)
	} else if (ev.state == "major") {
	    show_major(null)
	} else {
	    initial_tab()
	}
    }

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
}

function make_pointer(el, x, y1, y2, colour) {
    holderclass = ""
    if (y1 > y2) {
	holderclass = "pointer-xflip"
	var swap = y1
	y1 = y2
	y2 = swap
	y2 = y2 + 20
	y1 = y1 - 10
    }

    holderclass = holderclass + " pointer-" + colour

    if (y2 - y1 < 64) {
	var missing = 64 - (y2 - y1)
	    y2 = y2 + (missing / 2)
	    y1 = y1 - (missing / 2)
    }

    var holder_start = "<div class='" + holderclass + " pointer-holder' style='left: " + x + "px; top: " + y1 + "px; height: "+ (y2 - y1) + "px'>"
    var top_html = "<div class='pointer-top'></div>"
    var mid_html = "<div class='pointer-mid' style='top:32px; height:" + (y2 - y1 - 64) + "px'></div>"
    var bottom_html = "<div class='pointer-bottom' style='top:" + (y2 - y1 - 32) + "px'></div>"
    var holder_end = "</div>"
    var new_el = jQuery(holder_start + top_html + mid_html + bottom_html + holder_end)
    new_el.appendTo(el)
}

function make_pointers() {
    $('.pointer-holder').remove()

    var par = $('#late-reporting-column')
    var y1 = ($('#not-reported-bar').offset().top + $('#reported-bar').offset().top) / 2 - par.offset().top - 10
    var y2 = $('#chartcopy-brash-1').offset().top - par.offset().top + $('#chartcopy-brash-1').height() / 2 - 10 
    var x = $('#not-reported-bar').offset().left - par.offset().left - 30
    make_pointer(par, x, y1, y2, "default")

    par = $('#inconsistent-data-column')
    var y1 = $('#inconsistent-data-bar').offset().top - par.offset().top + $('#inconsistent-data-bar').height() / 2 + 10
    var y2 = $('#chartcopy-7').offset().top - par.offset().top + $('#chartcopy-7').height() / 2 - 10
    var x = $('#inconsistent-data-bar').offset().left - par.offset().left + $('#inconsistent-data-bar').width() + 30
    make_pointer(par, x, y2, y1, "grey")
}

$( window ).resize(function() {
    make_pointers()
});

function activate_charts() {
    /* Charts */
    Chart.defaults.global.defaultFontFamily = "Lato, 'Times New Roman', Times, serif"
    Chart.defaults.global.defaultFontSize = 15
    Chart.defaults.global.defaultFontColor = '#333'

    /* Pie chart 1 */
    var unreported_data = {
	labels: [ "Reported on time", "Late reporting results" ],
	datasets: [
	{
	    data: [total_due - total_unreported, total_unreported],
	    backgroundColor: [ "#343434", "#e95436" ],
	    hoverBackgroundColor: [ "#343434", "#e95436" ]
       	},
	]
    }
    var unreported_options = {
	legend: { display: false },
	animation: { animateRotate: false, duration: 0 },
    }
    var unreported_ctx = document.getElementById("unreported_chart");
    if (unreported_ctx) {
	window.unreported_chart = new Chart(unreported_ctx, {
	    type: 'pie' ,
	    data: unreported_data,
	    options: unreported_options
	});
    }

    /* Pointers on bar chart - needs to be done after document ready
       or has wrong sizes on Chrome */
    make_pointers()
    $(document).ready(make_pointers)
}




