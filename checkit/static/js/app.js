$(document).ready(() => {
  $('.alert').delay(5000).fadeOut(1000);

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

  $('.fa-cog').hover(function() {
    $(this).toggleClass('fa-spin');
  });
});

$(() => {
  $('[data-toggle="tooltip"]').tooltip();
  $('#date-field').datepicker();
});

function handlesearch(e) {
  if(e.keyCode !== 13) return;
  e.preventDefault();
  e.stopPropagation();

  let qstring = window.location.search;
  let qparams = new URLSearchParams(qstring);
  qparams.set('search', $('#search').val());
  window.location.search = qparams.toString();
}