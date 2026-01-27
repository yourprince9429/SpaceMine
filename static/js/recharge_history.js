;
(function() {
  // 获取DOM元素
  const listEl = document.getElementById('list');
  const sumAmtEl = document.getElementById('sumAmt');
  const sumCntEl = document.getElementById('sumCnt');
  const tabBtns = document.querySelectorAll('.tabs .btn');

  // 当前选中的状态
  let currentStatus = 'all';

  // 获取充值记录
  async function fetchRecharges(status = 'all') {
    try {
      const url = new URL('/api/user/recharges', window.location.origin);
      if (status !== 'all') {
        url.searchParams.append('status', status);
      }

      const response = await fetch(url);
      if (!response.ok) {
        throw new Error('获取充值记录失败');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('获取充值记录异常:', error);
      return {
        success: false,
        message: '获取充值记录失败'
      };
    }
  }

  // 渲染充值记录列表
  function renderRecharges(recharges) {
    if (!recharges.success || !recharges.list || recharges.list.length === 0) {
      listEl.innerHTML = '<div class="empty-state">暫無充值紀錄</div>';
      return;
    }

    const html = recharges.list.map(item => {
      // 根据状态设置徽章样式
      let badgeClass = '';
      let badgeText = '';

      switch (item.status) {
        case 'completed':
          badgeClass = 'bd-success';
          badgeText = '成功';
          break;
        case 'failed':
          badgeClass = 'bd-fail';
          badgeText = '失敗';
          break;
        case 'pending':
          badgeClass = 'bd-pending';
          badgeText = '待處理';
          break;
      }

      // 根据类型设置图标
      let iconSvg = '';
      if (item.type === 'CARD') {
        iconSvg =
          '<svg viewBox="0 0 24 24" width="26" height="26" fill="currentColor"><path d="M3 5h18a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2zm0 4h18V7H3zm0 2v6h18v-6z"/></svg>';
      } else {
        iconSvg =
          '<svg viewBox="0 0 24 24" width="26" height="26" fill="currentColor"><path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm1 11.73V17h-2v-3.27A7.23 7.23 0 0 1 5 10h14a7.23 7.23 0 0 1-6 3.73zM7 8V6h10v2Z"/></svg>';
      }

      return `
        <div class="item">
          <div class="logo">
            ${iconSvg}
          </div>
          <div class="meta">
            <div class="name">${item.type_name}</div>
            <div class="desc">訂單號：${item.order_id}</div>
          </div>
          <div class="side">
            <div class="amt">+${item.amount}</div>
            <div class="badge ${badgeClass}">${badgeText}</div>
          </div>
        </div>
      `;
    }).join('');

    listEl.innerHTML = html;
  }

  // 更新汇总信息
  function updateSummary(data) {
    if (data.success) {
      sumAmtEl.textContent = data.total_amount.toFixed(2);
      sumCntEl.textContent = data.total_count;
    }
  }

  // 加载充值记录
  async function loadRecharges() {
    listEl.innerHTML = '<div class="empty-state">載入中...</div>';

    const data = await fetchRecharges(currentStatus);
    updateSummary(data);
    renderRecharges(data);
  }

  // 初始化标签页事件
  function initTabs() {
    tabBtns.forEach(btn => {
      btn.addEventListener('click', async () => {
        // 更新选中状态
        tabBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // 更新当前状态并重新加载数据
        currentStatus = btn.dataset.s;
        await loadRecharges();
      });
    });
  }

  // 初始化
  function init() {
    initTabs();
    loadRecharges();
  }

  // 页面加载完成后初始化
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();