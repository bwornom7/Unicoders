$(document).ready(() => {
  $('.alert').delay(5000).fadeOut(1000);

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
});

$(() => {
  $('[data-toggle="tooltip"]').tooltip()
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