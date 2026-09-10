/* Landing site only (2026-09-09).
   THE FORM HAS NO BACKEND YET and must not pretend to. There is no domain, so
   FormSubmit cannot be activated, and a form that silently swallows a
   customer's details is worse than no form at all. So the submit builds a
   WhatsApp message from the fields and hands it to the customer to send: it
   works today, on the phone the shop already answers, with no server.
   When a domain exists, wire a real endpoint and delete this. */
(function () {
  var f = document.getElementById('lp-form');
  if (!f) return;
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    var v = function (id) { var el = document.getElementById(id); return el ? el.value.trim() : ''; };
    var lines = ['Hello, I would like a quote.'];
    if (v('lp-name')) lines.push('Name: ' + v('lp-name'));
    if (v('lp-phone')) lines.push('Phone: ' + v('lp-phone'));
    if (v('lp-job')) lines.push('Job: ' + v('lp-job'));
    var url = f.dataset.fallback + '?text=' + encodeURIComponent(lines.join('\n'));
    window.open(url, '_blank', 'noopener');
  });
})();
