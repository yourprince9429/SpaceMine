(function() {
  var style = document.createElement('style');
  style.textContent =
    "\n.ui-modal{position:fixed;inset:0;display:none;place-items:center;background:rgba(0,0,0,.55);z-index:9999}.ui-modal.is-open{display:grid}.ui-card{width:min(520px,94vw);border-radius:16px;overflow:hidden;background:#0f172a;color:#e6f0ff;box-shadow:0 12px 30px rgba(0,0,0,.5)}.ui-head{padding:14px 16px;font-size:16px;font-weight:700;background:rgba(255,255,255,.06)}.ui-body{padding:16px;font-size:14px;line-height:1.6}.ui-actions{padding:12px 16px;display:flex;justify-content:flex-end;gap:10px;background:rgba(255,255,255,.06)}.ui-btn{appearance:none;border:0;border-radius:10px;height:36px;padding:0 14px;cursor:pointer}.ui-btn.primary{background:linear-gradient(90deg,#88b6ff,#5aa0ff);color:#fff;box-shadow:0 6px 14px rgba(80,140,255,.35)}.ui-btn.secondary{background:rgba(255,255,255,.12);color:#cfe7ff;border:1px solid rgba(255,255,255,.18)}\n";
  document.head.appendChild(style);
  var modal = document.createElement('div');
  modal.className = 'ui-modal';
  modal.innerHTML =
    "<div class=\"ui-card\"><div class=\"ui-head\" id=\"uiTitle\">提示</div><div class=\"ui-body\" id=\"uiContent\"></div><div class=\"ui-actions\"><button class=\"ui-btn secondary\" id=\"uiCancel\">取消</button><button class=\"ui-btn primary\" id=\"uiOk\">確定</button></div></div>";
  document.body.appendChild(modal);
  var titleEl = modal.querySelector('#uiTitle');
  var contentEl = modal.querySelector('#uiContent');
  var okBtn = modal.querySelector('#uiOk');
  var cancelBtn = modal.querySelector('#uiCancel');

  function open() {
    modal.classList.add('is-open');
  }

  function close() {
    modal.classList.remove('is-open');
  }
  modal.addEventListener('click', function(e) {
    if (e.target === modal) close();
  });
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') close();
  });

  function uiAlert(msg, title) {
    titleEl.textContent = (title || '提示');
    contentEl.textContent = (msg || '');
    cancelBtn.style.display = 'none';
    okBtn.onclick = close;
    open();
  }

  function uiAlertThen(msg, title, onOk) {
    titleEl.textContent = (title || '提示');
    contentEl.textContent = (msg || '');
    cancelBtn.style.display = 'none';
    okBtn.onclick = function() {
      close();
      try {
        if (typeof onOk === 'function') onOk();
      } catch (e) {}
    };
    open();
  }

  function uiConfirm(msg, title) {
    return new Promise(function(resolve) {
      titleEl.textContent = (title || '確認');
      contentEl.textContent = (msg || '');
      cancelBtn.style.display = '';
      okBtn.onclick = function() {
        close();
        resolve(true);
      };
      cancelBtn.onclick = function() {
        close();
        resolve(false);
      };
      open();
    });
  }
  window.uiAlert = uiAlert;
  window.uiAlertThen = uiAlertThen;
  window.uiConfirm = uiConfirm;
  window.alert = uiAlert;
  try {
    var _f = window.fetch;
    if (typeof _f === 'function') {
      window.fetch = function(i, n) {
        return _f(i, n).then(function(res) {
          try {
            if (res && res.status === 401) {
              uiAlertThen('网络异常，请先登录。', '提示', function() {
                location.href = '/ui/login';
              });
            }
          } catch (e) {}
          return res;
        });
      };
    }
    var _j = Response && Response.prototype && Response.prototype.json;
    if (typeof _j === 'function') {
      Response.prototype.json = function() {
        return _j.call(this).then(function(d) {
          try {
            var ok = !(d && d.success === false);
            var msg = String((d && (d.error || d.msg)) || '');
            var need = (!ok && (msg.indexOf('未认') >= 0 || msg.indexOf('未認') >= 0 || msg
                .indexOf('会话') >= 0 || msg.indexOf('會話') >= 0 || msg.indexOf('过期') >= 0)) ||
              (String(d && d.code) === '-1' && (msg.indexOf('未登录') >= 0 || msg.indexOf(
                '請重新登') >= 0));
            if (need) {
              uiAlertThen('网络异常，请先登录。', '提示', function() {
                location.href = '/ui/login';
              });
            }
          } catch (e) {}
          return d;
        });
      };
    }
  } catch (e) {}
})();