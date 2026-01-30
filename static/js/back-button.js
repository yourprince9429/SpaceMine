(function() {
  function setupBackButton() {
    var src = new URLSearchParams(window.location.search).get('src') || '';
    src = src.trim();
    var backLink = document.getElementById('backLink');
    var backText = document.getElementById('backText');
    if (!backLink || !backText) {
      setTimeout(setupBackButton, 100);
      return;
    }

    var isAdminPage = window.location.pathname.includes('/admin');
    var isRechargeHistoryPage = window.location.pathname.includes('/ui/recharge/history');

    if (src === 'user' || isAdminPage || isRechargeHistoryPage) {
      backLink.href = '/dashboard#user';
      backLink.setAttribute('aria-label', '返回我的');
      backText.textContent = '返回我的';
    } else {
      backLink.href = '/dashboard';
      backLink.setAttribute('aria-label', '返回首页');
      backText.textContent = '返回首页';
    }
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupBackButton);
  } else {
    setupBackButton();
  }
})();