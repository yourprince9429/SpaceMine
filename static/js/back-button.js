(function() {
  function setupBackButton() {
    var src = new URLSearchParams(window.location.search).get('src') || '';
    src = src.trim();
    console.log('Back button src:', src);
    var backLink = document.getElementById('backLink');
    var backText = document.getElementById('backText');
    if (!backLink || !backText) {
      console.log('Back elements not found, retrying...');
      setTimeout(setupBackButton, 100);
      return;
    }

    var isAdminPage = window.location.pathname.includes('/admin');

    if (src === 'user' || isAdminPage) {
      backLink.href = '/dashboard#user';
      backLink.setAttribute('aria-label', '返回我的');
      backText.textContent = '返回我的';
      console.log('Set to 返回我的');
    } else {
      backLink.href = '/dashboard';
      backLink.setAttribute('aria-label', '返回首页');
      backText.textContent = '返回首页';
      console.log('Set to 返回首页');
    }
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupBackButton);
  } else {
    setupBackButton();
  }
})();