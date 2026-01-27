(function() {
  console.log('withdraw.page.js loaded');

  // 测试 uiAlertThen 是否可用
  if (typeof uiAlertThen === 'undefined') {
    console.error('uiAlertThen is not defined');
  } else {
    console.log('uiAlertThen is available');
  }

  // 基本的标签页切换功能
  const tabs = [...document.querySelectorAll('.tab')];
  const panels = {
    usdt: document.getElementById('panel-usdt'),
    bank: document.getElementById('panel-bank')
  };

  if (tabs.length > 0 && panels.usdt && panels.bank) {
    tabs.forEach(t => t.addEventListener('click', () => {
      tabs.forEach(x => x.classList.remove('active'));
      t.classList.add('active');
      Object.values(panels).forEach(p => p.classList.remove('active'));
      panels[t.dataset.key].classList.add('active');
    }));
  }

  // 数字键盘函数
  function showKeypad(title, onDone) {
    let ov = document.createElement('div');
    ov.innerHTML = (
      '<div class="keypad-mask"></div>' +
      '<div class="keypad">' +
      '<div class="kp-title">' + (title || '') + '</div>' +
      '<div class="kp-display">' +
      '<div class="kp-dot"></div><div class="kp-dot"></div><div class="kp-dot"></div>' +
      '<div class="kp-dot"></div><div class="kp-dot"></div><div class="kp-dot"></div>' +
      '</div>' +
      '<div class="kp-grid">' +
      '<button class="kp-key">1</button><button class="kp-key">2</button><button class="kp-key">3</button>' +
      '<button class="kp-key">4</button><button class="kp-key">5</button><button class="kp-key">6</button>' +
      '<button class="kp-key">7</button><button class="kp-key">8</button><button class="kp-key">9</button>' +
      '<button class="kp-key">⌫</button><button class="kp-key">0</button><button class="kp-key">✕</button>' +
      '</div>' +
      '<div class="kp-actions"><button class="kp-key">取消</button><button class="kp-key kp-primary">确认</button></div>' +
      '</div>'
    );
    document.body.appendChild(ov);
    const mask = ov.querySelector('.keypad-mask');
    mask.addEventListener('click', () => {
      ov.remove();
    });

    let val = '';
    const dots = ov.querySelectorAll('.kp-dot');

    function updateDots() {
      dots.forEach((d, i) => d.classList.toggle('filled', i < val.length));
    }

    ov.querySelectorAll('.kp-grid .kp-key').forEach(btn => btn.addEventListener('click', () => {
      const t = btn.textContent;
      if (t === '⌫') {
        val = val.slice(0, -1);
        updateDots();
        return;
      }
      if (t === '✕') {
        val = '';
        updateDots();
        return;
      }
      if (val.length < 6 && /\d/.test(t)) {
        val += t;
        updateDots();
      }
    }));

    const act = ov.querySelectorAll('.kp-actions .kp-key');
    act[0].addEventListener('click', () => {
      ov.remove();
    });
    act[1].addEventListener('click', () => {
      if (val.length !== 6) {
        alert('请输入6位数字密码');
        return;
      }
      try {
        onDone && onDone(val);
      } catch (e) {}
      ov.remove();
    });
  }

  // 为交易密码输入框添加点击事件
  const payPwdUsdt = document.getElementById('payPwdUsdt');
  if (payPwdUsdt) {
    payPwdUsdt.addEventListener('click', () => {
      showKeypad('请输入交易密码', v => {
        payPwdUsdt.value = v;
      });
    });
  }

  const payPwdBank = document.getElementById('payPwdBank');
  if (payPwdBank) {
    payPwdBank.addEventListener('click', () => {
      showKeypad('请输入交易密码', v => {
        payPwdBank.value = v;
      });
    });
  }

  // 加载提现信息
  async function loadInfo() {
    try {
      const r = await fetch('/ui/api/withdraw/info', {
        credentials: 'include'
      });
      const d = await r.json();
      if (!(d && d.success)) return;

      const availFood = document.getElementById('availFood');
      if (availFood) availFood.textContent = Number(d.available_food || 0).toFixed(2);

      const disable = Number(d.pending_count || 0) > 0;
      const su = document.getElementById('btnSubmitUsdt');
      const sb = document.getElementById('btnSubmitBank');

      if (su) {
        su.disabled = disable;
        su.style.opacity = disable ? .6 : 1;
      }
      if (sb) {
        sb.disabled = disable;
        sb.style.opacity = disable ? .6 : 1;
      }

      const pendingWarnUsdt = document.getElementById('pendingWarnUsdt');
      const pendingWarnBank = document.getElementById('pendingWarnBank');

      if (pendingWarnUsdt) pendingWarnUsdt.style.display = disable ? 'block' : 'none';
      if (pendingWarnBank) pendingWarnBank.style.display = disable ? 'block' : 'none';

      loadRecords('all');
    } catch (e) {
      console.error('Error loading info:', e);
    }
  }

  // 加载提现记录
  function loadRecords(f) {
    fetch('/ui/api/withdraw/list' + (f && f !== 'all' ? ('?status=' + encodeURIComponent(f)) :
        ''), {
          credentials: 'include'
        })
      .then(r => r.json())
      .then(d => {
        if (!(d && d.success)) return;
        const list = document.getElementById('recList');
        if (!list) return;

        list.innerHTML = '';
        const arr = d.list || [];
        if (arr.length === 0) {
          list.innerHTML = '<div style="text-align:center;color:#a8c4ff">暂无提现记录</div>';
          return;
        }

        arr.forEach(it => {
          const div = document.createElement('div');
          div.className = 'rec';
          const bc = it.status === 'success' ? 'badge bd-success' : (it.status === 'fail' ?
            'badge bd-fail' : 'badge bd-pending');

          let addressInfo = '';
          if (it.type_name === '银行卡提现' && it.address) {
            addressInfo = '<div style="font-size:11px; color:#a8c4ff; margin-top:2px;">' +
              it.address + '</div>';
          }

          div.innerHTML = '<div><div class="name">' + (it.type_name || '提现') +
            '</div><div class="time">创建时间：' + (it.created_at || '') + '</div>' +
            addressInfo + '</div>' +
            '<div class="right"><div class="amt">' + Number(it.amount || 0).toFixed(2) +
            '</div><div class="' + bc + '">' + (it.status_text || '待审核') + '</div></div>';
          list.appendChild(div);
        });
      })
      .catch(() => {});
  }

  // 网络类型选择
  let net = 'TRC20';
  const bTRC = document.getElementById('netTRC');
  const bERC = document.getElementById('netERC');

  if (bTRC && bERC) {
    function setNet(n) {
      net = n;
      bTRC.classList.toggle('active', n === 'TRC20');
      bERC.classList.toggle('active', n === 'ERC20');
    }

    setNet('TRC20');
    bTRC.addEventListener('click', () => setNet('TRC20'));
    bERC.addEventListener('click', () => setNet('ERC20'));
  }

  // 更新预计到账金额
  function updateEstimate() {
    const usdtAmt = parseFloatSafe(document.getElementById('usdtAmt')?.value);
    const bankAmt = parseFloatSafe(document.getElementById('bnAmt')?.value);

    const usdtEstimate = document.getElementById('usdtEstimate');
    const bankEstimate = document.getElementById('bankEstimate');

    if (usdtEstimate) usdtEstimate.textContent = (usdtAmt || 0).toFixed(2);
    if (bankEstimate) bankEstimate.textContent = (bankAmt || 0).toFixed(2);
  }

  function parseFloatSafe(v) {
    try {
      return parseFloat(v);
    } catch (e) {
      return NaN;
    }
  }

  // 事件监听器
  document.getElementById('btnAllUsdt')?.addEventListener('click', () => {
    const availFood = document.getElementById('availFood')?.textContent || '0';
    const usdtAmt = document.getElementById('usdtAmt');
    if (usdtAmt) usdtAmt.value = Math.floor(Number(availFood));
    updateEstimate();
  });

  document.getElementById('btnAllBank')?.addEventListener('click', () => {
    const availFood = document.getElementById('availFood')?.textContent || '0';
    const bnAmt = document.getElementById('bnAmt');
    if (bnAmt) bnAmt.value = Math.floor(Number(availFood));
    updateEstimate();
  });

  document.getElementById('usdtAmt')?.addEventListener('input', updateEstimate);
  document.getElementById('bnAmt')?.addEventListener('input', updateEstimate);

  // USDT提现提交
  document.getElementById('btnSubmitUsdt')?.addEventListener('click', async () => {
    const su = document.getElementById('btnSubmitUsdt');
    if (su && su.disabled) {
      alert('存在待审核申请，暂不可再次提交');
      return;
    }

    const addr = document.getElementById('usdtAddr')?.value.trim();
    const amt = parseFloatSafe(document.getElementById('usdtAmt')?.value);
    const p = (document.getElementById('payPwdUsdt')?.value || '').trim();

    if (!addr) {
      alert('请输入USDT地址');
      return;
    }
    if (!amt || isNaN(amt) || amt <= 0) {
      alert('请输入有效的提现能量');
      return;
    }
    if (!Number.isInteger(amt)) {
      alert('提现能量必须为整数');
      return;
    }
    if (!/^\d{6}$/.test(p)) {
      alert('交易密码必须为6位数字');
      return;
    }

    const availFood = document.getElementById('availFood')?.textContent || '0';
    if (amt > Math.floor(Number(availFood))) {
      alert('提现能量超过可用余额');
      return;
    }

    try {
      const res = await fetch('/ui/withdraw/usdt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          address: addr,
          network: net,
          amount: amt,
          pay_password: p
        })
      });
      const d = await res.json().catch(() => ({}));

      if (!(d && d.success)) {
        alert(d && d.error || '提交失败，请联系客服');
        return;
      }

      if (typeof uiAlertThen === 'function') {
        uiAlertThen('提现申请提交成功，请等待审核', '提示', () => {
          location.reload();
        });
      } else {
        alert('提现申请提交成功，请等待审核');
        location.reload();
      }
    } catch (e) {
      console.error('Error submitting USDT withdrawal:', e);
      alert('提交失败，请联系客服');
    }
  });

  // 银行卡提现提交
  document.getElementById('btnSubmitBank')?.addEventListener('click', async () => {
    const sb = document.getElementById('btnSubmitBank');
    if (sb && sb.disabled) {
      alert('存在待审核申请，暂不可再次提交');
      return;
    }

    const holder = document.getElementById('bnHolder')?.value.trim();
    const card = document.getElementById('bnCard')?.value.trim();
    const bank = document.getElementById('bnBank')?.value.trim();
    const code = document.getElementById('bnCode')?.value.trim();
    const amt = parseFloatSafe(document.getElementById('bnAmt')?.value);
    const p = (document.getElementById('payPwdBank')?.value || '').trim();

    if (!holder || !card || !bank || !code) {
      alert('请填写完整的银行卡信息');
      return;
    }
    if (!amt || isNaN(amt) || amt <= 0) {
      alert('请输入有效的提现能量');
      return;
    }
    if (!Number.isInteger(amt)) {
      alert('提现能量必须为整数');
      return;
    }
    if (!/^\d{6}$/.test(p)) {
      alert('交易密码必须为6位数字');
      return;
    }

    const availFood = document.getElementById('availFood')?.textContent || '0';
    if (amt > Math.floor(Number(availFood))) {
      alert('提现能量超过可用余额');
      return;
    }

    try {
      const res = await fetch('/ui/withdraw/bank', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          holder,
          card,
          bank,
          code,
          amount: amt,
          pay_password: p
        })
      });
      const d = await res.json().catch(() => ({}));

      if (!(d && d.success)) {
        alert(d && d.error || '提交失败，请联系客服');
        return;
      }

      if (typeof uiAlertThen === 'function') {
        uiAlertThen('提现申请提交成功，请等待审核', '提示', () => {
          location.reload();
        });
      } else {
        alert('提现申请提交成功，请等待审核');
        location.reload();
      }
    } catch (e) {
      console.error('Error submitting bank withdrawal:', e);
      alert('提交失败，请联系客服');
    }
  });

  // 返回按钮
  document.getElementById('btnBackUsdt')?.addEventListener('click', () => {
    location.href = '/#user';
  });

  document.getElementById('btnBackBank')?.addEventListener('click', () => {
    location.href = '/#user';
  });

  // 过滤器
  let filter = 'all';

  function setFilter(k) {
    document.querySelectorAll('[data-f]').forEach(x => {
      x.classList.toggle('active', x.dataset.f === k);
    });
  }

  document.querySelectorAll('[data-f]').forEach(b => b.addEventListener('click', (e) => {
    filter = e.currentTarget.dataset.f;
    setFilter(filter);
    loadRecords(filter);
  }));

  // 初始化
  loadInfo();
  setFilter(filter);

  console.log('withdraw.page.js initialized');
})();