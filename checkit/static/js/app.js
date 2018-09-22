$(document).ready(function() {
  $('.alert').delay(5000).fadeOut(1000);
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