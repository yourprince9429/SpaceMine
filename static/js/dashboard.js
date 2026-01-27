const buttons = document.querySelectorAll('.tabbar button');
const pages = {
  home: document.getElementById('page-home'),
  mine: document.getElementById('page-mine'),
  game: document.getElementById('page-game'),
  user: document.getElementById('page-user'),
};

function switchTo(key) {
  try {
    if (key !== 'mine' && window._mineTimers && Array.isArray(window._mineTimers)) {
      window._mineTimers.forEach(id => {
        try {
          clearInterval(id);
        } catch (e) {}
      });
      window._mineTimers = [];
    }
  } catch (e) {}
  if (key === 'game') {
    try {
      fetch('/api/security/verifyStatus').then(r => r.json()).then(d => {
        if (!(d && d.success) && !(d && d.verified)) {
          showVerifyPrompt();
          return;
        }
        if (!(d.verified)) {
          showVerifyPrompt();
          return;
        }
        Object.values(pages).forEach(p => {
          if (p) p.classList.remove('active');
        });
        if (pages[key]) pages[key].classList.add('active');
        buttons.forEach(b => b.classList.toggle('active', b.dataset.target === key));
        if (key !== 'home') {
          history.replaceState(null, null, '#' + key);
        } else {
          history.replaceState(null, null, location.pathname + location.search.replace(
            /[?&]tab=[^&]*/, ''));
        }
      }).catch(() => {
        showVerifyPrompt();
      });
    } catch (e) {
      showVerifyPrompt();
    }
    return;
  }
  Object.values(pages).forEach(p => {
    if (p) p.classList.remove('active');
  });
  if (pages[key]) pages[key].classList.add('active');
  buttons.forEach(b => b.classList.toggle('active', b.dataset.target === key));
  // Update URL hash for current tab
  if (key !== 'home') {
    history.replaceState(null, null, '#' + key);
  } else {
    history.replaceState(null, null, location.pathname + location.search.replace(/[?&]tab=[^&]*/,
      ''));
  }
  if (key === 'mine') {
    try {
      if (typeof loadMine === 'function') {
        loadMine();
        setTimeout(function() {
          if (typeof adjustMineUI === 'function') adjustMineUI();
        }, 30);
        var _mid = setInterval(function() {
          try {
            loadMine();
            if (typeof adjustMineUI === 'function') adjustMineUI();
          } catch (e) {}
        }, 60000);
        try {
          if (!window._mineTimers) window._mineTimers = [];
          window._mineTimers.push(_mid);
        } catch (e) {}
      }
    } catch (e) {}
  }
  if (key === 'user') {
    if (typeof loadUser === 'function') loadUser();
  }
  if (key === 'home') {
    try {
      window.dispatchEvent(new Event('resize'));
    } catch (e) {}
  }
}
buttons.forEach(b => b.addEventListener('click', () => switchTo(b.dataset.target)));

function initDefaultTab() {
  var hash = (location.hash || '').replace('#', '');
  var params = new URLSearchParams(location.search);
  var tab = params.get('tab');
  var target = pages[hash] ? hash : (pages[tab] ? tab : 'home');
  switchTo(target);
  if (target === 'user' && params.get('section') === 'recharge') {
    if (typeof initRechargeHistory === 'function') initRechargeHistory();
  }
}
window.addEventListener('hashchange', initDefaultTab);
initDefaultTab();

// ===== 首页轮播逻辑 =====
(function initCarousel() {
  const root = document.getElementById('homeCarousel');
  if (!root) return;
  const slides = Array.from(root.querySelectorAll('.slide'));
  const dots = root.querySelector('.dots');
  let current = 0;

  // 构建圆点
  slides.forEach((_, idx) => {
    const d = document.createElement('button');
    d.type = 'button';
    d.className = 'dot' + (idx === 0 ? ' active' : '');
    d.addEventListener('click', () => show(idx));
    dots.appendChild(d);
  });

  // 加载图片（如不存在则保留占位）
  slides.forEach(slide => {
    const url = slide.dataset.img;
    if (!url) return;
    const img = new Image();
    img.onload = () => {
      slide.style.backgroundImage = `url('${url}')`;
    };
    img.onerror = () => {
      /* 保留占位背景 */ };
    img.src = url;
  });

  function show(idx) {
    current = idx % slides.length;
    slides.forEach((s, i) => s.classList.toggle('current', i === current));
    dots.querySelectorAll('.dot').forEach((d, i) => d.classList.toggle('active', i === current));
  }

  // 初始显示
  show(0);
  // 自动轮播
  setInterval(() => show(current + 1), 4000);
})();

function showVerifyPrompt() {
  try {
    let m = document.getElementById('verifyPrompt');
    if (!m) {
      m = document.createElement('div');
      m.id = 'verifyPrompt';
      m.innerHTML = (
        '<div style="position:fixed;inset:0;background:rgba(0,0,0,.25);z-index:1000"></div>' +
        '<div style="position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);width:min(92vw,420px);border-radius:16px;background:rgba(42,62,102,.98);color:#e6f0ff;box-shadow:0 12px 30px rgba(0,0,0,.45);z-index:1001">' +
        '<div style="padding:14px 16px;font-weight:800;text-align:center">需要實名認證</div>' +
        '<div style="padding:0 16px 14px;text-align:center;color:#a8c4ff">請先完成實名認證後再進入遊戲</div>' +
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:0 16px 16px"><button id="vCancel" class="btn secondary" style="height:44px;border-radius:12px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.18);color:#cfe7ff">取消</button><button id="vGo" class="btn primary" style="height:44px;border-radius:12px;background:linear-gradient(90deg,#88b6ff,#5aa0ff);color:#fff">去認證</button></div>' +
        '</div>');
      document.body.appendChild(m);
      m.firstChild.addEventListener('click', () => {
        m.remove();
      });
      document.getElementById('vCancel').addEventListener('click', () => {
        m.remove();
      });
      document.getElementById('vGo').addEventListener('click', () => {
        location.href = '/ui/security';
      });
    }
  } catch (e) {}
}

// ===== 卡片组合动态等比贴齐 =====
(function fitCards() {
  const invite = document.getElementById('cardInvite');
  const games = document.getElementById('cardGames');
  const recharge = document.getElementById('cardRecharge');
  if (!invite || !games || !recharge) return;
  const imgInvite = invite.querySelector('img');
  const imgGames = games.querySelector('img');
  const imgRecharge = recharge.querySelector('img');

  function applySizes() {
    const iw = imgInvite.naturalWidth || imgInvite.width;
    const ih = imgInvite.naturalHeight || imgInvite.height;
    if (iw && ih) {
      // 左卡按实际纵横比设置容器比例，避免上下留白
      invite.style.aspectRatio = `${iw} / ${ih}`;
      // 右两卡高度各为左卡高度的一半，实现贴齐
      const leftWidth = invite.clientWidth;
      const leftHeight = leftWidth * (ih / iw);
      games.style.height = `${Math.max(0, Math.round(leftHeight / 2))}px`;
      recharge.style.height = `${Math.max(0, Math.round(leftHeight / 2))}px`;
    }
    // 右两卡也按自身素材比例填满各自容器
    if (imgGames.naturalWidth && imgGames.naturalHeight) {
      games.style.aspectRatio = `${imgGames.naturalWidth} / ${imgGames.naturalHeight}`;
    }
    if (imgRecharge.naturalWidth && imgRecharge.naturalHeight) {
      recharge.style.aspectRatio = `${imgRecharge.naturalWidth} / ${imgRecharge.naturalHeight}`;
    }
  }

  const ready = () => {
    applySizes();
    let tid;
    window.addEventListener('resize', () => {
      clearTimeout(tid);
      tid = setTimeout(applySizes, 100);
    });
    window.fitCardsApplySizes = applySizes;
  };
  const imgs = [imgInvite, imgGames, imgRecharge];
  let loaded = 0;
  imgs.forEach(img => {
    if (!img) return;
    if (img.complete && img.naturalWidth) {
      loaded++;
      if (loaded >= imgs.length) ready();
    } else img.addEventListener('load', () => {
      loaded++;
      if (loaded >= imgs.length) ready();
    }, {
      once: true
    });
  });
})();

// ===== 首页按钮占位事件 =====
// ===== 图片卡片点击事件 =====
var cardInvite = document.getElementById('cardInvite');
if (cardInvite) {
  cardInvite.addEventListener('click', () => {
    location.href = '/ui/invite?src=home';
  });
}
var cardRecharge = document.getElementById('cardRecharge');
if (cardRecharge) {
  cardRecharge.addEventListener('click', () => {
    location.href = '/recharge?src=home';
  });
}
var btnQuickRecharge = document.getElementById('btnQuickRecharge');
if (btnQuickRecharge) {
  btnQuickRecharge.addEventListener('click', function() {
    location.href = '/recharge?src=user';
  });
}
var cardGames = document.getElementById('cardGames');
if (cardGames) {
  cardGames.addEventListener('click', () => {
    switchTo('mine');
  });
}

function loadUser() {
  try {
    fetch('/api/invite/info').then(r => r.json()).then(d => {
      var name = (d && d.mobile) || '--';
      var code = (d && d.user_code) || '--';
      var nEl = document.getElementById('userName');
      if (nEl) nEl.textContent = name;
      var iEl = document.getElementById('userId');
      if (iEl) iEl.textContent = code;
    }).catch(() => {});
    fetch('/api/invite/summary').then(r => r.json()).then(d => {
      var rate = (d && d.rate) || 0;
      var cnt = (d && d.invited_count) || 0;
      var rEl = document.getElementById('metricRate');
      if (rEl) rEl.textContent = (rate + '/天');
      var cEl = document.getElementById('metricFriends');
      if (cEl) cEl.textContent = cnt;
    }).catch(() => {});

    fetch('/api/messages/unread').then(r => r.json()).then(d => {
      if (!(d && d.success)) return;
      var box = document.getElementById('msgList');
      if (!box) return;
      var arr = d.list || [];
      if (arr.length === 0) {
        box.innerHTML = '<div style="text-align:center;color:#a8c4ff">暫無未讀消息</div>';
        return;
      }
      box.innerHTML = '';
      arr.forEach(function(it) {
        var div = document.createElement('div');
        div.style.display = 'grid';
        div.style.gridTemplateColumns = '1fr auto';
        div.style.alignItems = 'center';
        div.style.gap = '10px';
        div.style.padding = '10px 12px';
        div.style.borderRadius = '12px';
        div.style.background = 'rgba(136,182,255,.18)';
        div.style.border = '1px solid rgba(136,182,255,.30)';
        div.innerHTML = '<div><div style="font-weight:700">' + (it.title || '') +
          '</div><div style="font-size:12px;color:#a8c4ff">' + (it.created_at || '') +
          '</div></div><div style="font-size:12px;color:#9fd1ff">查看</div>';
        div.addEventListener('click', function() {
          viewMessage(it.id);
        });
        box.appendChild(div);
      });
    }).catch(() => {});

    // 检查管理员角色并动态更新标签和添加管理系统按钮
    fetch('/api/user/role').then(r => r.json()).then(d => {
      if (d && d.success && d.is_admin) {
        // 更新角色标签
        var roleBadge = document.getElementById('userRoleBadge');
        if (roleBadge) {
          var text = roleBadge.querySelector('span:last-child');
          if (text) text.textContent = '管理员';
        }

        // 动态添加管理系统按钮
        var grid = document.querySelector('.quick-grid');
        if (grid && !document.getElementById('qAdminDynamic')) {
          var adminItem = document.createElement('a');
          adminItem.href = '/admin';
          adminItem.className = 'item';
          adminItem.id = 'qAdminDynamic';
          adminItem.innerHTML = `
                  <span class="icon">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2l8 4v6c0 5-3.5 9.74-8 10-4.5-.26-8-5-8-10V6l8-4zm0 2.5L5.5 7.5v4.5c0 3.5 2.5 7.5 6.5 8.5s6.5-4.5 6.5-8.5V7.5L12 4.5z"/>
                    </svg>
                  </span>
                  <span class="label">管理系统</span>
                `;
          grid.insertBefore(adminItem, grid.firstChild);
        }
      }
    }).catch(() => {});
  } catch (e) {}
}

function computeGained(a, tlist) {
  try {
    const t = (tlist || []).find(x => x.code === a.type_code);
    const cycle = t ? Number(t.cycle_days || 0) : 0;
    const total = Number(a.reward_energy || 0);
    const totalSecs = cycle * 24 * 3600;
    const start = Date.parse(a.start_time.replace(' ', 'T'));
    const now = Date.now();
    const elapsed = Math.max(0, Math.min((now - start) / 1000, totalSecs));
    const perSec = total / totalSecs;
    const val = elapsed * perSec;
    return Number(val.toFixed(6));
  } catch (e) {
    return 0;
  }
}
try {
  if (!window._mineTimers) {
    window._mineTimers = [];
  }
} catch (e) {}

function showFloatGain(box, gain, anchor) {
  const tip = document.createElement('div');
  tip.textContent = '+' + Number(gain).toFixed(6);
  tip.style.position = 'absolute';
  tip.style.color = '#9fd1ff';
  tip.style.fontWeight = '700';
  tip.style.transition = 'all 1.6s ease';
  let startX = box.clientWidth / 2;
  let startY = box.clientHeight / 2;
  try {
    if (!anchor) {
      anchor = box.querySelector('.mine-robot') || box.querySelector('img[src$="i65.gif"]');
    }
    if (anchor && anchor.getBoundingClientRect) {
      const ar = anchor.getBoundingClientRect();
      const br = box.getBoundingClientRect();
      startX = ar.left + ar.width / 2 - br.left;
      startY = ar.top + ar.height / 2 - br.top;
    }
  } catch (e) {}
  tip.style.left = startX + 'px';
  tip.style.top = startY + 'px';
  tip.style.transform = 'translate(-50%,-50%)';
  box.appendChild(tip);
  setTimeout(() => {
    tip.style.top = (startY - 100) + 'px';
    tip.style.opacity = '0';
  }, 10);
  setTimeout(() => {
    tip.remove();
  }, 1800);
}
async function loadMine() {
  try {
    try {
      if (window._mineTimers && Array.isArray(window._mineTimers)) {
        window._mineTimers.forEach(id => {
          try {
            clearInterval(id);
          } catch (e) {}
        });
        window._mineTimers = [];
      }
    } catch (e) {}
    const r = await fetch('/api/user/mines');
    const d = await r.json();
    if (!(d && d.success)) return;
    const rb = await fetch('/api/user/balance');
    const db = await rb.json();
    const minerCnt = document.getElementById('minerCnt');
    if (minerCnt) minerCnt.textContent = (db && db.success) ? db.balance : '--';
    const energyCube = document.getElementById('energyCube');
    if (energyCube) energyCube.textContent = (db && db.success) ? db.energy : '--';
    const list = document.getElementById('mineList');
    list.innerHTML = '';
    let totalEnergyPerSecond = 0;
    (d.mines || []).forEach(mine => {
      if (mine.is_activated) {
        totalEnergyPerSecond += parseFloat(mine.energy_per_second);
      }
      const div = document.createElement('div');
      div.className = 'mine-card';
      const bg = '/static/img/' + (mine.background_image || 'k1.png');
      div.innerHTML = '<img src="' + bg + '" alt="' + (mine.name || '') + '"/>';
      const overlay = document.createElement('div');
      overlay.className = 'mine-overlay';
      if (mine.is_activated) {
        const remDays = Math.max(0, Math.ceil(mine.cycle_days - mine.activated_duration /
          86400));
        overlay.innerHTML =
          '<div style="display:flex;justify-content:space-between;align-items:center"><div style="font-weight:700">' +
          mine.name + '</div></div><div style="margin-top:4px">累計：<span id="gotEnergy">' +
          mine.total_generated_energy + '</span>｜剩餘天數 ' + remDays + '｜' + mine
          .miners_consumed + ' 正在挖礦</div>';
        var _tid = setInterval(() => {
          const ge = overlay.querySelector('#gotEnergy');
          if (!ge) return;
          const newEnergy = parseFloat(mine.total_generated_energy) + parseFloat(mine
            .energy_per_second) * 4;
          const energyReward = parseFloat(mine.energy_reward) || 0;
          ge.textContent = newEnergy.toFixed(4);
          mine.total_generated_energy = newEnergy.toFixed(4);
          if (newEnergy >= energyReward) {
            loadMine();
          }
          const anchor = div.querySelector('img[src$="i65.gif"]');
          showFloatGain(div, parseFloat(mine.energy_per_second) * 4, anchor);
        }, 4000);
        try {
          window._mineTimers.push(_tid);
        } catch (e) {}
        const anim = document.createElement('img');
        anim.src = '/static/img/i65.gif';
        anim.style.position = 'absolute';
        anim.style.left = '50%';
        anim.style.top = '50%';
        anim.style.transform = 'translate(-50%,-50%)';
        anim.style.width = '42px';
        anim.style.height = '42px';
        div.appendChild(anim);
      } else {
        overlay.innerHTML = '<div>' + mine.name + '</div><div>消耗礦工：' + mine.miners_consumed +
          '｜週期：' + mine.cycle_days + '天｜產能：' + mine.energy_reward +
          '</div><div class="openMine">開啟</div>';
        const b = overlay.querySelector('.openMine');
        if (b) {
          b.addEventListener('click', async () => {
            const rr = await fetch('/api/mine/open', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              credentials: 'include',
              body: JSON.stringify({
                type_code: mine.code
              })
            });
            const dd = await rr.json().catch(() => ({}));
            if (!(dd && dd.success)) {
              alert(dd && dd.error || '操作異常，請聯繫客服');
              return;
            }
            loadMine();
          });
        }
      }
      div.appendChild(overlay);
      list.appendChild(div);
    });
    if (totalEnergyPerSecond > 0) {
      const energyCube = document.getElementById('energyCube');
      if (energyCube) {
        var _energyTimer = setInterval(() => {
          const currentEnergy = parseFloat(energyCube.textContent) || 0;
          const newEnergy = currentEnergy + totalEnergyPerSecond * 4;
          energyCube.textContent = newEnergy.toFixed(4);
        }, 4000);
        try {
          window._mineTimers.push(_energyTimer);
        } catch (e) {}
      }
    }
  } catch (e) {}
}
var btnOpen = document.getElementById('btnMineOpen');
if (btnOpen) {
  btnOpen.addEventListener('click', async () => {
    const r = await fetch('/api/user/mines');
    const d = await r.json();
    if (!(d && d.success)) return;
    const rb = await fetch('/api/user/balance');
    const db = await rb.json();
    if (!(db && db.success)) return;
    const can = d.mines.find(m => !m.is_activated && parseFloat(db.balance) >= parseFloat(m
      .miners_consumed));
    if (!can) {
      showAlert('可用礦工不足，請進行充值');
      return;
    }
    const rr = await fetch('/api/mine/open', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({
        type_code: can.code
      })
    });
    const dd = await rr.json().catch(() => ({}));
    if (!(dd && dd.success)) {
      const msg = (dd && dd.error) || '';
      if (msg.indexOf('礦工數不足') >= 0) {
        showAlert('可用礦工不足，請進行充值');
      } else if (msg.indexOf('該類型已在挖礦') >= 0) {
        showAlert('該類型已在挖礦，請稍後再試');
      } else {
        showAlert(msg || '操作異常，請聯繫客服');
      }
      return;
    }
    showAlert('開啟成功');
    loadMine();
  });
}
// 加载矿场数据在切换到矿场时
function adjustMineUI() {
  try {
    document.querySelectorAll('[id^="btnClaim_"]').forEach(function(el) {
      try {
        el.remove();
      } catch (e) {}
    });
    document.querySelectorAll('.mine-card .openMine').forEach(function(b) {
      try {
        b.style.right = '16px';
        b.style.bottom = '16px';
        b.style.left = 'auto';
        b.style.top = 'auto';
        b.style.transform = 'none';
      } catch (e) {}
    });
    document.querySelectorAll('.mine-card img[src$="i65.gif"]').forEach(function(img) {
      try {
        img.classList.add('mine-robot');
      } catch (e) {}
    });
  } catch (e) {}
}
(function() {
  const btn = document.querySelector('.tabbar button[data-target="mine"]');
  if (btn) {
    btn.addEventListener('click', function() {
      loadMine();
      setTimeout(adjustMineUI, 30);
    });
  }
})();
var bInv = document.getElementById('btnInvite');
if (bInv) {
  bInv.addEventListener('click', function() {
    location.href = '/ui/invite?src=user';
  });
}
var bSet = document.getElementById('btnSettings');
if (bSet) {
  bSet.addEventListener('click', async function() {
    try {
      await fetch('/api/logout', {
        method: 'POST'
      });
    } catch (e) {}
    try {
      localStorage.removeItem('X-Session-Token');
      document.cookie = 'X-Session-Token=; Max-Age=0; path=/';
    } catch (e) {}
    location.href = '/ui/login';
  });
}
var q1 = document.getElementById('qRecharge');
if (q1) {
  q1.addEventListener('click', function() {
    location.href = '/ui/recharge/history';
  });
}
var q2 = document.getElementById('qWithdraw');
if (q2) {
  q2.addEventListener('click', function() {
    location.href = '/ui/withdraw';
  });
}
var q3 = document.getElementById('qSecurity');
if (q3) {
  q3.addEventListener('click', function() {
    location.href = '/ui/security';
  });
}
var q4 = document.getElementById('qVerify');
if (q4) {
  q4.addEventListener('click', function() {
    alert('功能即將上線');
  });
}
var q5 = document.getElementById('qPrivacy');
if (q5) {
  q5.addEventListener('click', function() {
    alert('功能即將上線');
  });
}
var q6 = document.getElementById('qService');
if (q6) {
  q6.addEventListener('click', async function() {
    try {
      const r = await fetch('/api/support/info');
      const d = await r.json();
      const emails = (d && d.success && d.emails) || [];
      showSupportModal(emails);
    } catch (e) {
      showSupportModal([]);
    }
  });
}
var qi = document.getElementById('qIntro');
if (qi) {
  qi.addEventListener('click', function() {
    location.href = '/ui/intro';
  });
}
var qn = document.getElementById('qNotices');
if (qn) {
  qn.addEventListener('click', function() {
    location.href = '/ui/notices';
  });
}
var vAll = document.getElementById('viewAllMsg');
if (vAll) {
  vAll.addEventListener('click', function() {
    location.href = '/ui/messages';
  });
}
var mRule = document.getElementById('btnMineRule');
if (mRule) {
  mRule.addEventListener('click', async function() {
    try {
      const r = await fetch('/api/user/mines');
      const d = await r.json();
      showMineRules(d.mines || []);
    } catch (e) {
      showMineRules([]);
    }
  });
}

function showAlert(message) {
  try {
    let modal = document.getElementById('uiAlert');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'uiAlert';
      modal.innerHTML = `
        <div class="support-mask" style="position:fixed;inset:0;background:rgba(0,0,0,.25);z-index:1000"></div>
        <div class="support-dialog" style="position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);width:min(90vw,420px);border-radius:16px;background:rgba(42,62,102,.98);color:#e6f0ff;box-shadow:0 12px 30px rgba(0,0,0,.45);z-index:1001">
          <div style="padding:14px 16px;font-weight:800;text-align:center">提示</div>
          <div id="uiAlertMsg" style="padding:0 16px 14px;text-align:center;color:#cfe7ff;word-break:break-word"></div>
          <div style="display:flex;justify-content:center;padding:0 16px 16px"><button id="uiAlertOk" class="btn primary" style="height:40px;border-radius:12px;background:linear-gradient(90deg,#88b6ff,#5aa0ff);color:#fff;padding:0 18px">知道了</button></div>
        </div>
      `;
      document.body.appendChild(modal);
      const mask = modal.querySelector('.support-mask');
      mask.addEventListener('click', () => {
        modal.remove();
      });
      modal.querySelector('#uiAlertOk').addEventListener('click', () => {
        modal.remove();
      });
    }
    const box = document.getElementById('uiAlertMsg');
    box.textContent = String(message || '');
  } catch (e) {}
}
try {
  if (!window._native_alert) {
    window._native_alert = window.alert;
    window.alert = function(m) {
      try {
        showAlert(String(m || ''));
      } catch (e) {
        try {
          window._native_alert(String(m || ''));
        } catch (e2) {}
      }
    };
  }
} catch (e) {}

function showMineRules(types) {
  try {
    let modal = document.getElementById('mineRules');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'mineRules';
      modal.innerHTML = `
        <div class="support-mask" style="position:fixed;inset:0;background:rgba(0,0,0,.25);z-index:1000"></div>
        <div class="support-dialog" style="position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);width:min(90vw,420px);border-radius:16px;background:rgba(42,62,102,.98);color:#e6f0ff;box-shadow:0 12px 30px rgba(0,0,0,.45);z-index:1001">
          <div style="padding:14px 16px;font-weight:800;text-align:center">礦場規則</div>
          <div id="ruleList" style="display:grid;gap:10px;padding:0 16px 16px"></div>
        </div>
      `;
      document.body.appendChild(modal);
      modal.querySelector('.support-mask').addEventListener('click', () => {
        modal.remove();
      });
    }
    const box = document.getElementById('ruleList');
    box.innerHTML = '';
    if (!types || types.length === 0) {
      box.innerHTML = '<div style="text-align:center;color:#a8c4ff">暫無規則</div>';
      return;
    }
    types.forEach(t => {
      const row = document.createElement('div');
      row.style.display = 'grid';
      row.style.gridTemplateColumns = '1fr auto';
      row.style.gap = '8px';
      row.style.alignItems = 'center';
      row.style.background = 'rgba(255,255,255,.12)';
      row.style.border = '1px solid rgba(255,255,255,.22)';
      row.style.borderRadius = '12px';
      row.style.padding = '10px 12px';
      row.innerHTML = '<div><div style="font-weight:700">' + t.name +
        '</div><div style="font-size:12px;color:#a8c4ff">消耗礦工：' + t.miners_consumed + '｜週期：' + t
        .cycle_days + '天｜回報能量：' + Number(t.energy_reward).toFixed(6) + '</div></div>';
      box.appendChild(row);
    });
  } catch (e) {}
}

function showSupportModal(list) {
  try {
    let modal = document.getElementById('supportModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'supportModal';
      modal.innerHTML = `
        <div class="support-mask" style="position:fixed;inset:0;background:rgba(0,0,0,.25);z-index:1000"></div>
        <div class="support-dialog" style="position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);width:min(90vw,420px);border-radius:16px;background:rgba(42,62,102,.98);color:#e6f0ff;box-shadow:0 12px 30px rgba(0,0,0,.45);z-index:1001">
          <div style="padding:14px 16px;font-weight:800;text-align:center">聯繫客服</div>
          <div style="padding:0 16px 14px;text-align:center;color:#a8c4ff">請通過以下郵箱聯繫我們</div>
          <div id="supportList" style="display:grid;gap:10px;padding:0 16px 16px"></div>
        </div>
      `;
      document.body.appendChild(modal);
      const mask = modal.querySelector('.support-mask');
      mask.addEventListener('click', () => {
        modal.remove();
      });
    }
    const box = document.getElementById('supportList');
    box.innerHTML = '';
    const data = (Array.isArray(list) && list.filter(Boolean)) || [];
    if (data.length === 0) {
      box.innerHTML = '<div style="text-align:center;color:#a8c4ff">暫無客服郵箱</div>';
      return;
    }
    data.forEach((em) => {
      const row = document.createElement('div');
      row.style.display = 'grid';
      row.style.gridTemplateColumns = '1fr auto';
      row.style.gap = '8px';
      row.style.alignItems = 'center';
      row.style.background = 'rgba(255,255,255,.12)';
      row.style.border = '1px solid rgba(255,255,255,.22)';
      row.style.borderRadius = '12px';
      row.style.padding = '10px 12px';
      row.innerHTML =
        '<div style="display:flex;align-items:center;gap:8px"><span style="line-height:0;color:#88b6ff"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M20 4H4a2 2 0 0 0-2 2v12l6-4h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2z"/></svg></span><span style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis" class="copyable">' +
        em +
        '</span></div><button class="copyBtn" style="appearance:none;border:0;border-radius:10px;padding:8px 12px;background:#ff7b2e;color:#fff;box-shadow:0 4px 10px rgba(255,123,46,.35)">複製</button>';
      const btn = row.querySelector('.copyBtn');
      const span = row.querySelector('.copyable');
      btn.addEventListener('click', () => {
        const txt = em;
        try {
          navigator.clipboard.writeText(txt).then(() => {
            btn.textContent = '已複製';
            setTimeout(() => btn.textContent = '複製', 1500);
          }).catch(() => {
            throw new Error('no');
          });
        } catch (e) {
          try {
            const ta = document.createElement('textarea');
            ta.value = txt;
            ta.style.position = 'fixed';
            ta.style.left = '-9999px';
            document.body.appendChild(ta);
            ta.focus();
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
            btn.textContent = '已複製';
            setTimeout(() => btn.textContent = '複製', 1500);
          } catch (e2) {
            alert('複製失敗');
          }
        }
      });
      box.appendChild(row);
    });
  } catch (e) {}
}

function viewMessage(messageId) {
  fetch(`/api/messages/${messageId}`)
    .then(response => response.json())
    .then(data => {
      if (data.success && data.message) {
        showMessageDetail(data.message);

        if (!data.message.is_read) {
          markAsRead(messageId);
        }
      } else {
        showAlert(data.error || '获取消息详情失败');
      }
    })
    .catch(error => {
      console.error('查看消息失败:', error);
      showAlert('查看消息失败，请稍后重试');
    });
}

function markAsRead(messageId) {
  fetch(`/api/messages/${messageId}/read`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        const box = document.getElementById('msgList');
        if (box) {
          fetch('/api/messages/unread').then(r => r.json()).then(d => {
            if (!(d && d.success)) return;
            var arr = d.list || [];
            if (arr.length === 0) {
              box.innerHTML = '<div style="text-align:center;color:#a8c4ff">暫無未讀消息</div>';
              return;
            }
            box.innerHTML = '';
            arr.forEach(function(it) {
              var div = document.createElement('div');
              div.style.display = 'grid';
              div.style.gridTemplateColumns = '1fr auto';
              div.style.alignItems = 'center';
              div.style.gap = '10px';
              div.style.padding = '10px 12px';
              div.style.borderRadius = '12px';
              div.style.background = 'rgba(136,182,255,.18)';
              div.style.border = '1px solid rgba(136,182,255,.30)';
              div.innerHTML = '<div><div style="font-weight:700">' + (it.title || '') +
                '</div><div style="font-size:12px;color:#a8c4ff">' + (it.created_at ||
                '') + '</div></div><div style="font-size:12px;color:#9fd1ff">查看</div>';
              div.addEventListener('click', function() {
                viewMessage(it.id);
              });
              box.appendChild(div);
            });
          }).catch(() => {});
        }
      }
    })
    .catch(error => {
      console.error('标记已读失败:', error);
    });
}

function showMessageDetail(message) {
  let modal = document.getElementById('messageDetailModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'messageDetailModal';
    modal.innerHTML = `
            <div class="support-mask" style="position:fixed;inset:0;background:rgba(0,0,0,.25);z-index:1000"></div>
            <div class="support-dialog" style="position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);width:min(90vw,420px);max-height:80vh;overflow-y:auto;border-radius:16px;background:rgba(42,62,102,.98);color:#e6f0ff;box-shadow:0 12px 30px rgba(0,0,0,.45);z-index:1001">
              <div style="padding:14px 16px;font-weight:800;text-align:center;border-bottom:1px solid rgba(255,255,255,.15)" id="messageTitle"></div>
              <div style="padding:12px 16px 14px;color:#cfe7ff;white-space:pre-wrap;word-break:break-word" id="messageContent"></div>
              <div style="padding:0 16px 14px;text-align:center;color:#a8c4ff;font-size:12px" id="messageTime"></div>
              <div style="display:flex;justify-content:center;padding:0 16px 16px"><button id="messageCloseBtn" class="btn primary" style="height:40px;border-radius:12px;background:linear-gradient(90deg,#88b6ff,#5aa0ff);color:#fff;padding:0 18px">关闭</button></div>
            </div>
          `;
    document.body.appendChild(modal);
    const mask = modal.querySelector('.support-mask');
    mask.addEventListener('click', () => {
      modal.remove();
    });
    modal.querySelector('#messageCloseBtn').addEventListener('click', () => {
      modal.remove();
    });
  }

  modal.querySelector('#messageTitle').textContent = message.title || '';
  modal.querySelector('#messageContent').textContent = message.content || '';
  modal.querySelector('#messageTime').textContent = message.created_at || '';
}