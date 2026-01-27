;
(function() {
  var src = new URLSearchParams(window.location.search).get('src') || '';
  var u = document.getElementById('goUsdt');
  if (u) {
    u.addEventListener('click', function() {
      location.href = '/recharge/usdt' + (src ? '?src=' + src : '');
    });
  }
  var c = document.getElementById('goCard');
  if (c) {
    c.addEventListener('click', function() {
      location.href = '/recharge/card' + (src ? '?src=' + src : '');
    });
  }
})();