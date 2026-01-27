;
(function() {
  function S() {
    var t = (localStorage.getItem('X-Session-Token') || '').trim();
    fetch('/api/invite/summary', {
      headers: t ? {
        'X-Session-Token': t
      } : {}
    }).then(function(r) {
      return r.json().catch(function() {
        return {};
      });
    }).then(function(j) {
      if (!j || !j.success) return;
      document.getElementById('todayReward').textContent = (j.today_reward || '0.0000');
      document.getElementById('totalReward').textContent = (j.total_reward || '0.0000');
      document.getElementById('teamIncome').textContent = (j.team_income || '0.0000');
      document.getElementById('rate').textContent = ((j.rate || 0) + '%');
      document.getElementById('friendLine').textContent = '我的好友：' + (j.invited_count || 0) +
        ' 人';
    });
    fetch('/api/invite/users', {
      headers: t ? {
        'X-Session-Token': t
      } : {}
    }).then(function(r) {
      return r.json().catch(function() {
        return {};
      });
    }).then(function(j) {
      if (!j || !j.success) {
        document.getElementById('usersList').innerHTML =
          '<div class="empty-state">暫無邀請記錄</div>';
        return;
      }
      var users = j.users || [];
      if (users.length === 0) {
        document.getElementById('usersList').innerHTML =
          '<div class="empty-state">暫無邀請記錄</div>';
        return;
      }
      var html = '<div class="user-list">';
      for (var i = 0; i < users.length; i++) {
        var u = users[i];
        var nickname = u.user_nickname || u.mobile || '未知用户';
        var mobile = u.mobile || '';
        var balance = u.balance || '0.00';
        var addTime = u.add_time || '';
        html += '<div class="user-item">';
        html += '<div class="user-info">';
        html += '<div class="user-name">' + nickname + '</div>';
        html += '<div class="user-mobile">' + mobile + '</div>';
        html += '</div>';
        html += '<div class="user-stats">';
        html += '<div class="user-balance">餘額：' + balance + '</div>';
        html += '<div class="user-time">' + addTime + '</div>';
        html += '</div>';
        html += '</div>';
      }
      html += '</div>';
      document.getElementById('usersList').innerHTML = html;
    });
  }
  var b = document.getElementById('btnInvite');
  if (b) {
    b.addEventListener('click', function() {
      var t = (localStorage.getItem('X-Session-Token') || '');
      var h = t ? {
        'X-Session-Token': t
      } : {};
      fetch('/api/invite/info', {
        headers: h,
        credentials: 'include'
      }).then(function(r) {
        return r.json();
      }).catch(function() {
        return {};
      }).then(function(info) {
        if (!(info && info.success)) {
          alert('网络异常，请先登录。');
          return;
        }
        var m = document.getElementById('shareModal');
        document.getElementById('shareName').textContent = (info.mobile || '') + '';
        document.getElementById('shareCode').textContent = '邀請碼：' + (info.user_code ||
        '');
        var q = document.getElementById('shareQrImg');
        q.onerror = function() {
          q.src = '/ui/invite/qr?size=200x200';
        };
        q.src = '/ui/invite/qr?size=200x200';
        m.classList.add('is-open');
      });
    });
  }
  var c = document.getElementById('shareClose');
  if (c) {
    c.addEventListener('click', function() {
      document.getElementById('shareModal').classList.remove('is-open');
    });
  }
  S();
  (function() {
    function setupBackButton() {
      var src = new URLSearchParams(window.location.search).get('src') || '';
      src = src.trim();
      console.log('Invite page src:', src);
      var backLink = document.getElementById('backLink');
      var backText = document.getElementById('backText');
      if (!backLink || !backText) {
        console.log('Back elements not found, retrying...');
        setTimeout(setupBackButton, 100);
        return;
      }
      if (src === 'user') {
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
})();