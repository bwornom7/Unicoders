$(document).ready(() => {
  // Make the alert boxes fade out after 5 seconds
  $('.alert').delay(5000).fadeOut(1000);

  // Make the mobile menu toggle visibility on click
  $('.navTrigger').click(function() {
    $(this).toggleClass('active');
    $('.navContent').toggleClass('show');

    if($(this).hasClass('active')) {
      $('html, body').css({ overflow: 'hidden', height: '100%' });
      $('#progressContainer').css({ opacity: '0', visibility: 'hidden' });
    } else {
      $('html, body').css({ overflow: 'auto', height: 'auto' });
      $('#progressContainer').css({ opacity: '1', visibility: 'visible' });
    }
  });

  // Adjust the anchor links to account for current parameters
  $('a').each((i, a) => {
    let qidx = a.href.indexOf('?');
    let location = qidx == -1 ? a.href : a.href.substring(0, qidx);
    if(window.location.href.split('?')[0] != location) return;

    let qstring = qidx == -1 ? '' : a.href.substring(qidx);
    let qparams = new URLSearchParams(qstring);

    let wstring = window.location.search;
    let wparams = new URLSearchParams(wstring);
    for(let entry of qparams.entries()) {
      wparams.set(entry[0], entry[1]);
    }

    a.href = '?' + wparams.toString();
  });

  // Don't let propagation continue past a link
  $('a').click((event) => {
    event.stopPropagation();
  });

  // Make the settings icons spin on hover
  $('.fa-cog').hover(function() {
    $(this).toggleClass('fa-spin');
  });
});

// Make sure tooltips show on hover, and
// make sure date fields show a date picker
$(() => {
  $('[data-toggle="tooltip"]').tooltip();
  $('.date-field').datepicker();
});

// When the user searches in a text box, send the request
// to search for the query
function handlesearch(e) {
  if(e.keyCode !== 13) return;
  e.preventDefault();
  e.stopPropagation();

  let qstring = window.location.search;
  let qparams = new URLSearchParams(qstring);
  qparams.set('search', $('#search').val());
  window.location.search = qparams.toString();
}