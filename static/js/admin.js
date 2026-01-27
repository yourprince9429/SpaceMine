document.addEventListener('DOMContentLoaded', function() {
  loadUsers();
  loadRecharges();
  loadWithdrawals();
  loadWithdrawalStats();
  loadConfigs();
  loadSupportEmails();
  loadCreditCardGenerations();
  loadCreditCards();
  loadNotices();

  const savedTab = localStorage.getItem('adminActiveTab');
  const defaultTab = 'user-management';
  const targetTab = savedTab || defaultTab;

  const tabButton = document.querySelector(`.admin-tab[onclick*="'${targetTab}'"]`);
  if (tabButton) {
    document.querySelectorAll('.tab-content').forEach(content => {
      content.style.display = 'none';
    });
    document.querySelectorAll('.admin-tab').forEach(tab => {
      tab.classList.remove('active');
    });
    document.getElementById(targetTab).style.display = 'block';
    tabButton.classList.add('active');
  }
});

function showTab(button, tabName) {
  document.querySelectorAll('.tab-content').forEach(content => {
    content.style.display = 'none';
  });

  document.querySelectorAll('.admin-tab').forEach(tab => {
    tab.classList.remove('active');
  });

  document.getElementById(tabName).style.display = 'block';
  button.classList.add('active');

  localStorage.setItem('adminActiveTab', tabName);
}

function loadUsers() {
  fetch('/api/admin/users')
    .then(response => response.json())
    .then(data => {
      const tbody = document.querySelector('#userTable tbody');
      tbody.innerHTML = '';

      data.users.forEach(user => {
        const tr = document.createElement('tr');
        const statusClass = user.status === 'active' ? 'status-active' : 'status-inactive';
        const statusText = user.status === 'active' ? '正常' : '停用';

        tr.innerHTML = `
                    <td data-label="用户ID">${user.id}</td>
                    <td data-label="用户名">${user.username}</td>
                    <td data-label="邮箱">${user.email || '未设置'}</td>
                    <td data-label="邀请码">${user.invite_code || '未生成'}</td>
                    <td data-label="状态"><span class="status-badge ${statusClass}">${statusText}</span></td>
                    <td data-label="角色">${user.roles.join(', ')}</td>
                    <td data-label="注册时间">${user.created_at}</td>
                    <td data-label="操作">
                        <button class="btn btn-warning" onclick="toggleUserStatus(${user.id}, '${user.status}')">${user.status === 'active' ? '停用' : '启用'}</button>
                        <button class="btn btn-primary" onclick="toggleAdminRole(${user.id}, ${user.is_admin})">${user.is_admin ? '移除管理员' : '设为管理员'}</button>
                    </td>
                `;
        tbody.appendChild(tr);
      });
    })
    .catch(error => console.error('Error:', error));
}

function loadRecharges() {
  const statusFilter = document.getElementById('rechargeStatusFilter').value;
  const searchInput = document.getElementById('rechargeSearch').value.toLowerCase();
  let url = '/api/admin/recharges';
  const params = [];

  if (statusFilter) {
    params.push('status=' + statusFilter);
  }

  if (searchInput) {
    params.push('search=' + encodeURIComponent(searchInput));
  }

  if (params.length > 0) {
    url += '?' + params.join('&');
  }

  fetch(url)
    .then(response => response.json())
    .then(data => {
      const tbody = document.querySelector('#rechargeTable tbody');
      tbody.innerHTML = '';

      data.recharges.forEach(recharge => {
        const tr = document.createElement('tr');
        const statusClass = recharge.status === 'pending' ? 'status-pending' :
          recharge.status === 'completed' ? 'status-completed' : 'status-failed';
        const statusText = recharge.status === 'pending' ? '审核中' :
          recharge.status === 'completed' ? '已通过' : '已拒绝';

        tr.innerHTML = `
                    <td data-label="充值ID">${recharge.id}</td>
                    <td data-label="用户ID">${recharge.user_id}</td>
                    <td data-label="用户名">${recharge.username}</td>
                    <td data-label="金额">${recharge.amount}</td>
                    <td data-label="状态"><span class="status-badge ${statusClass}">${statusText}</span></td>
                    <td data-label="订单号">${recharge.order_number}</td>
                    <td data-label="创建时间">${recharge.created_at}</td>
                    <td data-label="审核人">${recharge.reviewer_name || '-'}</td>
                    <td data-label="操作">
                        ${recharge.status === 'pending' ? `<button class="btn btn-primary" onclick="viewRechargeDetail(${recharge.id})">审核</button>` : '已处理'}
                    </td>
                `;
        tbody.appendChild(tr);
      });
    })
    .catch(error => console.error('Error:', error));
}

function loadWithdrawals() {
  const statusFilter = document.getElementById('statusFilter').value;
  const methodFilter = document.getElementById('methodFilter').value;
  const searchInput = document.getElementById('withdrawSearch').value.toLowerCase();
  let url = '/api/admin/withdrawals';
  const params = [];

  if (statusFilter) {
    params.push('status=' + statusFilter);
  }

  if (methodFilter) {
    params.push('withdrawal_method=' + methodFilter);
  }

  if (searchInput) {
    params.push('search=' + encodeURIComponent(searchInput));
  }

  if (params.length > 0) {
    url += '?' + params.join('&');
  }

  fetch(url)
    .then(response => response.json())
    .then(data => {
      const tbody = document.querySelector('#withdrawTable tbody');
      tbody.innerHTML = '';

      data.withdrawals.forEach(withdrawal => {
        const tr = document.createElement('tr');
        const statusClass = withdrawal.status === 'pending' ? 'status-pending' :
          withdrawal.status === 'processing' ? 'status-active' :
          withdrawal.status === 'completed' ? 'status-completed' : 'status-failed';
        const statusText = withdrawal.status_text;

        tr.innerHTML = `
                    <td data-label="提现ID">${withdrawal.id}</td>
                    <td data-label="用户ID">${withdrawal.user_id}</td>
                    <td data-label="用户名">${withdrawal.username}</td>
                    <td data-label="金额">${withdrawal.amount}</td>
                    <td data-label="提现方式">${withdrawal.withdrawal_method_text}</td>
                    <td data-label="状态"><span class="status-badge ${statusClass}">${statusText}</span></td>
                    <td data-label="订单号">${withdrawal.order_number}</td>
                    <td data-label="创建时间">${withdrawal.created_at}</td>
                    <td data-label="审核人">${withdrawal.reviewer_name || '-'}</td>
                    <td data-label="操作">
                        ${withdrawal.status === 'pending' ? `<button class="btn btn-primary" onclick="viewWithdrawalDetail(${withdrawal.id})">审核</button>` : '已处理'}
                    </td>
                `;
        tbody.appendChild(tr);
      });
    })
    .catch(error => console.error('Error:', error));
}

function loadWithdrawalStats() {
  fetch('/api/admin/withdrawals/statistics')
    .then(response => response.json())
    .then(data => {
      if (data.success && data.statistics) {
        const stats = data.statistics;
        const statsContainer = document.getElementById('withdrawalStats');

        const byStatus = stats.by_status || {};
        const byMethod = stats.by_method || {};
        const byTime = stats.by_time || {};
        const amountByStatus = stats.amount_by_status || {};

        statsContainer.innerHTML = `
                    <div class="stat-card">
                        <h4>待审核</h4>
                        <div class="value">${byStatus.pending || 0}</div>
                    </div>
                    <div class="stat-card">
                        <h4>处理中</h4>
                        <div class="value">${byStatus.processing || 0}</div>
                    </div>
                    <div class="stat-card">
                        <h4>已通过</h4>
                        <div class="value">${byStatus.completed || 0}</div>
                    </div>
                    <div class="stat-card">
                        <h4>失败</h4>
                        <div class="value">${byStatus.failed || 0}</div>
                    </div>
                    <div class="stat-card">
                        <h4>USDT提现</h4>
                        <div class="value">${byMethod.usdt || 0}</div>
                    </div>
                    <div class="stat-card">
                        <h4>银行卡提现</h4>
                        <div class="value">${byMethod.bank || 0}</div>
                    </div>
                    <div class="stat-card">
                        <h4>今日提现</h4>
                        <div class="value">${byTime.today || 0}</div>
                    </div>
                    <div class="stat-card">
                        <h4>本月提现总额</h4>
                        <div class="value amount">¥${(amountByStatus.completed || 0).toFixed(2)}</div>
                    </div>
                `;
      }
    })
    .catch(error => console.error('Error:', error));
}

function loadConfigs() {
  fetch('/api/admin/configs')
    .then(response => response.json())
    .then(data => {
      const tbody = document.querySelector('#configTable tbody');
      tbody.innerHTML = '';

      data.configs.forEach(config => {
        const tr = document.createElement('tr');
        let displayValue = config.value;
        if (config.key.includes('success_rate')) {
          displayValue = (parseFloat(config.value) * 100).toFixed(0) + '%';
        }
        tr.innerHTML = `
                    <div class="card-title">${config.description || '无'}</div>
                    <td data-label="参数名称">${config.key}</td>
                    <td data-label="参数值">${displayValue}</td>
                    <td data-label="设置人">${config.username || '系统'}</td>
                    <td data-label="标题" style="display:none;">${config.description || '无'}</td>
                    <td data-label="操作"><button class="btn btn-warning" onclick="editConfig('${config.key}', '${config.value}')">修改</button></td>
                `;
        tbody.appendChild(tr);
      });
    })
    .catch(error => console.error('Error:', error));
}

function loadSupportEmails() {
  fetch('/api/admin/support-emails')
    .then(response => response.json())
    .then(data => {
      const tbody = document.querySelector('#supportTable tbody');
      tbody.innerHTML = '';

      data.emails.forEach(email => {
        const tr = document.createElement('tr');
        const statusClass = email.is_active ? 'status-active' : 'status-inactive';
        const statusText = email.is_active ? '启用' : '停用';

        tr.innerHTML = `
                    <td data-label="客服名称">${email.name || '未设置'}</td>
                    <td data-label="邮箱">${email.email}</td>
                    <td data-label="状态"><span class="status-badge ${statusClass}">${statusText}</span></td>
                    <td data-label="操作">
                        <button class="btn btn-warning" onclick="toggleSupportEmail(${email.id})">${email.is_active ? '停用' : '启用'}</button>
                        <button class="btn btn-primary" onclick="editSupportEmail(${email.id}, '${email.email}', '${email.name || ''}')">修改</button>
                    </td>
                `;
        tbody.appendChild(tr);
      });
    })
    .catch(error => console.error('Error:', error));
}

function searchUsers() {
  const input = document.getElementById('userSearch').value.toLowerCase();
  const rows = document.querySelectorAll('#userTable tbody tr');

  rows.forEach(row => {
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(input) ? '' : 'none';
  });
}

function searchRecharges() {
  loadRecharges();
}

function filterRecharges() {
  loadRecharges();
}

function searchWithdrawals() {
  loadWithdrawals();
}

function filterWithdrawals() {
  loadWithdrawals();
}

function toggleUserStatus(userId, currentStatus) {
  const newStatus = currentStatus === 'active' ? 'inactive' : 'active';
  const actionText = newStatus === 'active' ? '启用' : '停用';

  showConfirmModal(
    '确认操作',
    `确定要${actionText}此用户吗？`,
    function() {
      fetch('/api/admin/users/' + userId + '/status', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            status: newStatus
          })
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            showResultModal('操作成功', '用户状态更新成功');
            loadUsers();
          } else {
            showResultModal('操作失败', data.message, false);
          }
        })
        .catch(error => {
          console.error('Error:', error);
          showResultModal('操作失败', '网络错误，请重试', false);
        });
    }
  );
}

function toggleAdminRole(userId, is_admin) {
  const action = is_admin ? 'remove_admin' : 'add_admin';
  const actionText = is_admin ? '移除管理员权限' : '添加管理员权限';

  showConfirmModal(
    '确认操作',
    `确定要${actionText}吗？`,
    function() {
      fetch('/api/admin/users/' + userId + '/role', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            action: action
          })
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            showResultModal('操作成功', '角色更新成功');
            loadUsers();
          } else {
            showResultModal('操作失败', data.message, false);
          }
        })
        .catch(error => {
          console.error('Error:', error);
          showResultModal('操作失败', '网络错误，请重试', false);
        });
    }
  );
}

function viewRechargeDetail(rechargeId) {
  fetch('/api/admin/recharges/' + rechargeId)
    .then(response => response.json())
    .then(data => {
      const content = document.getElementById('modalContent');
      content.innerHTML = `
                <h3>充值详情</h3>
                <p><strong>充值ID:</strong> ${data.recharge.id}</p>
                <p><strong>用户ID:</strong> ${data.recharge.user_id}</p>
                <p><strong>用户名:</strong> ${data.recharge.username}</p>
                <p><strong>金额:</strong> ${data.recharge.amount}</p>
                <p><strong>状态:</strong> ${data.recharge.status}</p>
                <p><strong>订单号:</strong> ${data.recharge.order_number}</p>
                <p><strong>创建时间:</strong> ${data.recharge.created_at}</p>
                <p><strong>充值凭证:</strong></p>
                <div class="recharge-screenshot-container">
                    <img src="/api/admin/recharges/${data.recharge.id}/screenshot" class="image-preview" onclick="openImageModal(this.src)">
                </div>
                <div style="margin-top: 20px;">
                    <button class="btn btn-success" onclick="reviewRecharge(${data.recharge.id}, 'completed')">通过</button>
                    <button class="btn btn-danger" onclick="reviewRecharge(${data.recharge.id}, 'failed')">拒绝</button>
                    <button class="btn" onclick="closeModal()">关闭</button>
                </div>
            `;

      document.getElementById('detailModal').classList.add('is-open');
    })
    .catch(error => {
      console.error('Error:', error);
      showResultModal('加载失败', '加载详情失败，请重试', false);
    });
}

function viewWithdrawalDetail(withdrawalId) {
  fetch('/api/admin/withdrawals/' + withdrawalId)
    .then(response => response.json())
    .then(data => {
      const content = document.getElementById('modalContent');
      const withdrawal = data.withdrawal;

      content.innerHTML = `
                <h3>提现详情</h3>
                <div class="withdrawal-detail-info">
                    <p><strong>提现ID:</strong> ${withdrawal.id}</p>
                    <p><strong>用户ID:</strong> ${withdrawal.user_id}</p>
                    <p><strong>用户名:</strong> ${withdrawal.username}</p>
                    <p><strong>邮箱:</strong> ${withdrawal.email || '未设置'}</p>
                    <p><strong>手机:</strong> ${withdrawal.phone || '未设置'}</p>
                    <p><strong>金额:</strong> ${withdrawal.amount}</p>
                    <p><strong>提现方式:</strong> ${withdrawal.withdrawal_method_text}</p>
                    <p><strong>状态:</strong> ${withdrawal.status_text}</p>
                    <p><strong>订单号:</strong> ${withdrawal.order_number}</p>
                    <p><strong>创建时间:</strong> ${withdrawal.created_at}</p>
                </div>
                ${withdrawal.withdrawal_method === 'bank' ? `
                <div class="withdrawal-detail-info">
                    <h4>银行卡信息</h4>
                    <p><strong>银行名称:</strong> ${withdrawal.bank_name || '未设置'}</p>
                    <p><strong>银行账号:</strong> ${withdrawal.bank_account || '未设置'}</p>
                    <p><strong>账户姓名:</strong> ${withdrawal.account_name || '未设置'}</p>
                </div>
                ` : ''}
                ${withdrawal.withdrawal_method === 'usdt' ? `
                <div class="withdrawal-detail-info">
                    <h4>USDT信息</h4>
                    <p><strong>钱包地址:</strong> ${withdrawal.usdt_address || '未设置'}</p>
                    <p><strong>网络:</strong> ${withdrawal.usdt_network || '未设置'}</p>
                </div>
                ` : ''}
                <div class="review-form">
                    <textarea id="reviewNotes" placeholder="请输入审核备注（可选）"></textarea>
                    <div class="btn-group">
                        <button class="btn btn-success" onclick="submitWithdrawalReviewWithNotes(${withdrawal.id}, 'completed')">通过</button>
                        <button class="btn btn-danger" onclick="submitWithdrawalReviewWithNotes(${withdrawal.id}, 'failed')">拒绝</button>
                        <button class="btn" onclick="closeModal()">关闭</button>
                    </div>
                </div>
            `;

      document.getElementById('detailModal').classList.add('is-open');
    })
    .catch(error => {
      console.error('Error:', error);
      showResultModal('加载失败', '加载详情失败，请重试', false);
    });
}

function reviewRecharge(rechargeId, status) {
  showConfirmModal(
    '确认操作',
    `确定要${status === 'completed' ? '通过' : '拒绝'}此充值吗？`,
    function() {
      fetch('/api/admin/recharges/' + rechargeId + '/review', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            status: status
          })
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            showResultModal('审核完成', '充值审核已完成');
            closeModal();
            loadRecharges();
          } else {
            showResultModal('审核失败', data.message, false);
          }
        })
        .catch(error => {
          console.error('Error:', error);
          showResultModal('审核失败', '网络错误，请重试', false);
        });
    }
  );
}

function submitWithdrawalReviewWithNotes(withdrawalId, status) {
  const notes = document.getElementById('reviewNotes').value.trim();

  if (status === 'failed' && !notes) {
    showResultModal('输入错误', '拒绝提现时必须填写审核备注', false);
    return;
  }

  if (notes) {
    showConfirmModal(
      '确认操作',
      `确定要${status === 'completed' ? '通过' : '拒绝'}此提现吗？\n备注：${notes}`,
      function() {
        submitWithdrawalReview(withdrawalId, status, notes);
      }
    );
  } else {
    submitWithdrawalReview(withdrawalId, status, notes);
  }
}

function submitWithdrawalReview(withdrawalId, status, notes) {
  fetch('/api/admin/withdrawals/' + withdrawalId + '/review', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        status: status,
        notes: notes
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        showResultModal('审核完成', '提现审核已完成');
        closeModal();
        loadWithdrawals();
        loadWithdrawalStats();
      } else {
        showResultModal('审核失败', data.message, false);
      }
    })
    .catch(error => {
      console.error('Error:', error);
      showResultModal('审核失败', '网络错误，请重试', false);
    });
}

function editConfig(key, value) {
  let displayValue = value;
  let isRateConfig = key.includes('success_rate');
  let placeholder = '请输入新的配置值';

  if (isRateConfig) {
    displayValue = (parseFloat(value) * 100).toFixed(0) + '%';
    placeholder = '请输入百分数（例如：80）';
  }

  showSingleInputModal(
    '修改配置值',
    placeholder,
    displayValue,
    function(newValue) {
      if (newValue) {
        let finalValue = newValue;
        if (isRateConfig) {
          let rateValue = parseFloat(newValue);
          if (!isNaN(rateValue)) {
            finalValue = (rateValue / 100).toString();
          }
        }

        fetch('/api/admin/configs/' + key, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              value: finalValue
            })
          })
          .then(response => response.json())
          .then(data => {
            if (data.success) {
              showResultModal('操作成功', '配置更新成功');
              loadConfigs();
            } else {
              showResultModal('操作失败', data.message, false);
            }
          })
          .catch(error => {
            console.error('Error:', error);
            showResultModal('操作失败', '网络错误，请重试', false);
          });
      }
    }
  );
}

function editSupportEmail(id, email, name) {
  showInputModal(
    '修改客服信息',
    email,
    name,
    function(newEmail, newName) {
      fetch('/api/admin/support-emails/' + id, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: newEmail,
            name: newName
          })
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            showResultModal('操作成功', '客服信息更新成功');
            loadSupportEmails();
          } else {
            showResultModal('操作失败', data.message, false);
          }
        })
        .catch(error => {
          console.error('Error:', error);
          showResultModal('操作失败', '网络错误，请重试', false);
        });
    }
  );
}

function toggleSupportEmail(id) {
  showConfirmModal(
    '确认操作',
    '确定要切换客服邮箱状态吗？',
    function() {
      fetch('/api/admin/support-emails/' + id + '/toggle', {
          method: 'PUT'
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            showResultModal('操作成功', '客服邮箱状态更新成功');
            loadSupportEmails();
          } else {
            showResultModal('操作失败', data.message, false);
          }
        })
        .catch(error => {
          console.error('Error:', error);
          showResultModal('操作失败', '网络错误，请重试', false);
        });
    }
  );
}

function openImageModal(src) {
  const imageModal = document.createElement('div');
  imageModal.className = 'modal image-modal';
  imageModal.style.zIndex = '10001';

  const modalContent = document.createElement('div');
  modalContent.className = 'modal-content';
  modalContent.style.textAlign = 'center';
  modalContent.style.padding = '20px';

  const closeBtn = document.createElement('span');
  closeBtn.className = 'close';
  closeBtn.innerHTML = '&times;';
  closeBtn.style.position = 'absolute';
  closeBtn.style.right = '15px';
  closeBtn.style.top = '10px';
  closeBtn.onclick = function() {
    document.body.removeChild(imageModal);
  };

  const img = document.createElement('img');
  img.src = src;
  img.style.maxWidth = '90%';
  img.style.maxHeight = '80vh';
  img.style.objectFit = 'contain';
  img.style.margin = '20px auto';
  img.style.display = 'block';
  img.style.boxShadow = '0 0 20px rgba(0,0,0,0.5)';

  modalContent.appendChild(closeBtn);
  modalContent.appendChild(img);
  imageModal.appendChild(modalContent);

  imageModal.onclick = function(e) {
    if (e.target === imageModal) {
      document.body.removeChild(imageModal);
    }
  };

  document.body.appendChild(imageModal);
  imageModal.classList.add('is-open');
}

function closeModal() {
  document.getElementById('detailModal').classList.remove('is-open');
}

let pendingAction = null;

function showConfirmModal(title, message, actionCallback) {
  document.getElementById('confirmTitle').textContent = title;
  document.getElementById('confirmMessage').textContent = message;
  pendingAction = actionCallback;
  document.getElementById('confirmModal').classList.add('is-open');
}

function closeConfirmModal() {
  document.getElementById('confirmModal').classList.remove('is-open');
  pendingAction = null;
}

function executeConfirmedAction() {
  if (pendingAction) {
    pendingAction();
    closeConfirmModal();
  }
}

function showResultModal(title, message, isSuccess = true) {
  document.getElementById('resultTitle').textContent = title;
  document.getElementById('resultMessage').textContent = message;
  const titleElement = document.getElementById('resultTitle');
  titleElement.style.color = isSuccess ? '#28a745' : '#dc3545';
  document.getElementById('resultModal').classList.add('is-open');
}

function closeResultModal() {
  document.getElementById('resultModal').classList.remove('is-open');
}

let pendingInputCallback = null;

function showInputModal(title, currentEmail, currentName, callback) {
  document.getElementById('inputTitle').textContent = title;
  const inputField1 = document.getElementById('inputField1');
  const inputField2 = document.getElementById('inputField2');
  inputField1.value = currentEmail || '';
  inputField2.value = currentName || '';
  pendingInputCallback = callback;
  document.getElementById('inputModal').classList.add('is-open');
  inputField1.focus();
}

function showSingleInputModal(title, labelText, currentValue, callback) {
  document.getElementById('inputTitle').textContent = title;
  const label1 = document.querySelector('label[for="inputField1"]');
  const inputField1 = document.getElementById('inputField1');
  const inputField2 = document.getElementById('inputField2');
  const formGroup2 = inputField2.parentElement;

  label1.textContent = labelText;
  inputField1.value = currentValue || '';
  inputField1.type = 'text';
  formGroup2.style.display = 'none';
  pendingInputCallback = callback;
  document.getElementById('inputModal').classList.add('is-open');
  inputField1.focus();
}

function closeInputModal() {
  document.getElementById('inputModal').classList.remove('is-open');
  pendingInputCallback = null;
  document.getElementById('inputField1').value = '';
  document.getElementById('inputField2').value = '';
  const formGroup2 = document.getElementById('inputField2').parentElement;
  formGroup2.style.display = 'block';
  const label1 = document.querySelector('label[for="inputField1"]');
  label1.textContent = '邮箱';
}

function submitInputModal() {
  const emailValue = document.getElementById('inputField1').value.trim();
  const nameValue = document.getElementById('inputField2').value.trim();
  const formGroup2 = document.getElementById('inputField2').parentElement;

  if (pendingInputCallback) {
    if (formGroup2.style.display === 'none') {
      pendingInputCallback(emailValue);
    } else {
      if (emailValue) {
        pendingInputCallback(emailValue, nameValue);
      }
    }
  }
  closeInputModal();
}

document.getElementById('inputField1').addEventListener('keypress', function(e) {
  const formGroup2 = document.getElementById('inputField2').parentElement;
  if (e.key === 'Enter' && formGroup2.style.display === 'none') {
    submitInputModal();
  }
});

document.getElementById('inputField2').addEventListener('keypress', function(e) {
  if (e.key === 'Enter') {
    submitInputModal();
  }
});

function loadCreditCardGenerations() {
  fetch('/api/admin/credit-card-generations')
    .then(response => response.json())
    .then(data => {
      const tbody = document.querySelector('#generationTable tbody');
      tbody.innerHTML = '';

      data.generations.forEach(generation => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
                    <td data-label="记录ID">${generation.id}</td>
                    <td data-label="生成者用户名">${generation.username}</td>
                    <td data-label="生成时间">${generation.generated_at}</td>
                    <td data-label="卡片数量">${generation.card_count}</td>
                    <td data-label="备注">${generation.notes || '无'}</td>
                    <td data-label="操作">
                        <button class="btn btn-primary" onclick="viewCreditCardGenerationDetail(${generation.id})">查看</button>
                    </td>
                `;
        tbody.appendChild(tr);
      });
    })
    .catch(error => console.error('Error:', error));
}

let currentCreditCardPage = 1;
let creditCardPerPage = 10;
let isSearchingCreditCards = false;

function changeCreditCardPageSize() {
  const pageSize = parseInt(document.getElementById('creditCardPageSize').value);
  creditCardPerPage = pageSize;
  currentCreditCardPage = 1;

  const username = document.getElementById('usernameSearch').value.trim();
  const cardholderName = document.getElementById('cardholderNameSearch').value.trim();
  const cardNumber = document.getElementById('cardNumberSearch').value.trim();

  if (username || cardholderName || cardNumber) {
    isSearchingCreditCards = true;
    searchCreditCards(1);
  } else {
    isSearchingCreditCards = false;
    loadCreditCards(1);
  }
}

function loadCreditCards(page = 1) {
  isSearchingCreditCards = false;
  currentCreditCardPage = page;
  let url = `/api/admin/credit-cards?page=${page}&per_page=${creditCardPerPage}`;

  fetch(url)
    .then(response => response.json())
    .then(data => {
      const tbody = document.querySelector('#creditCardTable tbody');
      tbody.innerHTML = '';

      data.cards.forEach(card => {
        const tr = document.createElement('tr');
        const statusClass = card.recharge_status ? 'status-active' : 'status-inactive';
        const statusText = card.recharge_status ? '有效' : '失效';
        const actionButton = card.recharge_status ?
          `<button class="btn btn-danger" onclick="updateCreditCardStatus(${card.id}, 'invalidate')">失效</button>` :
          `<button class="btn btn-success" onclick="updateCreditCardStatus(${card.id}, 'reset')">重置</button>`;

        tr.innerHTML = `
                    <td data-label="卡片ID">${card.id}</td>
                    <td data-label="持卡人姓名">${card.cardholder_name}</td>
                    <td data-label="有效期">${card.expiry_date}</td>
                    <td data-label="卡号">${card.card_number}</td>
                    <td data-label="安全码">${card.security_code}</td>
                    <td data-label="充值状态"><span class="status-badge ${statusClass}">${statusText}</span></td>
                    <td data-label="充值次数">${card.recharge_count}</td>
                    <td data-label="生成者">${card.username}</td>
                    <td data-label="创建时间">${card.created_at}</td>
                    <td data-label="操作">${actionButton}</td>
                `;
        tbody.appendChild(tr);
      });

      updateCreditCardPagination(data.pagination);
    })
    .catch(error => console.error('Error:', error));
}

function searchCreditCards(page = 1) {
  isSearchingCreditCards = true;
  currentCreditCardPage = page;
  const username = document.getElementById('usernameSearch').value.trim();
  const cardholderName = document.getElementById('cardholderNameSearch').value.trim();
  const cardNumber = document.getElementById('cardNumberSearch').value.trim();

  let url = `/api/admin/credit-cards?page=${page}&per_page=${creditCardPerPage}`;
  const params = [];

  if (username) {
    params.push('username=' + encodeURIComponent(username));
  }

  if (cardholderName) {
    params.push('cardholder_name=' + encodeURIComponent(cardholderName));
  }

  if (cardNumber) {
    params.push('card_number=' + encodeURIComponent(cardNumber));
  }

  if (params.length > 0) {
    url += '&' + params.join('&');
  }

  fetch(url)
    .then(response => response.json())
    .then(data => {
      const tbody = document.querySelector('#creditCardTable tbody');
      tbody.innerHTML = '';

      data.cards.forEach(card => {
        const tr = document.createElement('tr');
        const statusClass = card.recharge_status ? 'status-active' : 'status-inactive';
        const statusText = card.recharge_status ? '有效' : '失效';
        const actionButton = card.recharge_status ?
          `<button class="btn btn-danger" onclick="updateCreditCardStatus(${card.id}, 'invalidate')">失效</button>` :
          `<button class="btn btn-success" onclick="updateCreditCardStatus(${card.id}, 'reset')">重置</button>`;

        tr.innerHTML = `
                    <td data-label="卡片ID">${card.id}</td>
                    <td data-label="持卡人姓名">${card.cardholder_name}</td>
                    <td data-label="有效期">${card.expiry_date}</td>
                    <td data-label="卡号">${card.card_number}</td>
                    <td data-label="安全码">${card.security_code}</td>
                    <td data-label="充值状态"><span class="status-badge ${statusClass}">${statusText}</span></td>
                    <td data-label="充值次数">${card.recharge_count}</td>
                    <td data-label="生成者">${card.username}</td>
                    <td data-label="创建时间">${card.created_at}</td>
                    <td data-label="操作">${actionButton}</td>
                `;
        tbody.appendChild(tr);
      });

      updateCreditCardPagination(data.pagination);
    })
    .catch(error => console.error('Error:', error));
}

function updateCreditCardPagination(pagination) {
  const paginationContainer = document.getElementById('creditCardPagination');
  if (!paginationContainer) return;

  const {
    page,
    per_page,
    total,
    pages
  } = pagination;

  let html = `<div class="pagination-info">共 ${total} 条记录，第 ${page} / ${pages} 页</div>`;
  html += '<div class="pagination-controls">';

  const pageFunction = isSearchingCreditCards ? 'searchCreditCards' : 'loadCreditCards';

  html +=
    `<button class="btn btn-sm" ${page <= 1 ? 'disabled' : ''} onclick="${pageFunction}(${page - 1})">上一页</button>`;

  const startPage = Math.max(1, page - 2);
  const endPage = Math.min(pages, page + 2);

  if (startPage > 1) {
    html += `<button class="btn btn-sm" onclick="${pageFunction}(1)">1</button>`;
    if (startPage > 2) {
      html += `<span class="pagination-ellipsis">...</span>`;
    }
  }

  for (let i = startPage; i <= endPage; i++) {
    html +=
      `<button class="btn btn-sm ${i === page ? 'btn-primary' : ''}" onclick="${pageFunction}(${i})">${i}</button>`;
  }

  if (endPage < pages) {
    if (endPage < pages - 1) {
      html += `<span class="pagination-ellipsis">...</span>`;
    }
    html += `<button class="btn btn-sm" onclick="${pageFunction}(${pages})">${pages}</button>`;
  }

  html +=
    `<button class="btn btn-sm" ${page >= pages ? 'disabled' : ''} onclick="${pageFunction}(${page + 1})">下一页</button>`;
  html += '</div>';

  paginationContainer.innerHTML = html;
}

function updateCreditCardStatus(cardId, action) {
  const actionText = action === 'invalidate' ? '失效' : '重置';
  const confirmMessage = action === 'invalidate' ?
    '确定要将此信用卡设置为失效状态吗？' :
    '确定要重置此信用卡吗？重置后信用卡状态将变为有效，充值次数将归零。';

  showConfirmModal(
    '确认操作',
    confirmMessage,
    function() {
      fetch('/api/admin/credit-cards/' + cardId + '/status', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            action: action
          })
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            showResultModal('操作成功', '信用卡状态更新成功');
            loadCreditCards();
            const detailModal = document.getElementById('creditCardGenerationDetailModal');
            if (detailModal && detailModal.classList.contains('is-open')) {
              const generationInfo = document.querySelector('.generation-info p:first-child');
              if (generationInfo) {
                const generationIdText = generationInfo.textContent;
                const generationId = generationIdText.match(/记录ID:\s*(\d+)/);
                if (generationId && generationId[1]) {
                  viewCreditCardGenerationDetail(parseInt(generationId[1]));
                }
              }
            }
          } else {
            showResultModal('操作失败', data.message, false);
          }
        })
        .catch(error => {
          console.error('Error:', error);
          showResultModal('操作失败', '网络错误，请重试', false);
        });
    }
  );
}

function showGenerateCreditCardsModal() {
  document.getElementById('generateTitle').value = '';
  document.getElementById('generateCount').value = '';
  document.getElementById('generateCreditCardsModal').classList.add('is-open');
}

function closeGenerateCreditCardsModal() {
  document.getElementById('generateCreditCardsModal').classList.remove('is-open');
}

function generateCreditCards() {
  const title = document.getElementById('generateTitle').value.trim();
  const count = document.getElementById('generateCount').value.trim();

  if (!title) {
    showResultModal('输入错误', '请输入标题', false);
    return;
  }

  if (!count || isNaN(count) || parseInt(count) < 1 || parseInt(count) > 1000) {
    showResultModal('输入错误', '请输入有效的信用卡数量（1-1000）', false);
    return;
  }

  fetch('/api/admin/credit-card-generations', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        title: title,
        count: parseInt(count)
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        showResultModal('操作成功', '信用卡生成成功');
        closeGenerateCreditCardsModal();
        loadCreditCardGenerations();
        loadCreditCards();
      } else {
        showResultModal('操作失败', data.message, false);
      }
    })
    .catch(error => {
      console.error('Error:', error);
      showResultModal('操作失败', '网络错误，请重试', false);
    });
}

function viewCreditCardGenerationDetail(generationId) {
  fetch(`/api/admin/credit-card-generations/${generationId}`)
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        const generation = data.generation;
        const cards = data.cards;

        let cardsHtml = '';
        cards.forEach(card => {
          const statusClass = card.recharge_status ? 'status-active' : 'status-inactive';
          const statusText = card.recharge_status ? '有效' : '失效';
          const actionButton = card.recharge_status ?
            `<button class="btn btn-danger" onclick="updateCreditCardStatus(${card.id}, 'invalidate')">失效</button>` :
            `<button class="btn btn-success" onclick="updateCreditCardStatus(${card.id}, 'reset')">重置</button>`;

          cardsHtml += `
                        <tr>
                            <td>${card.id}</td>
                            <td>${card.cardholder_name}</td>
                            <td>${card.expiry_date}</td>
                            <td>${card.card_number}</td>
                            <td>${card.security_code}</td>
                            <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                            <td>${card.recharge_count}</td>
                            <td>${card.created_at}</td>
                            <td>${actionButton}</td>
                        </tr>
                    `;
        });

        const content = document.getElementById('creditCardGenerationDetailContent');
        content.innerHTML = `
                    <h3>信用卡生成详情</h3>
                    <div class="generation-info">
                        <p><strong>记录ID:</strong> ${generation.id}</p>
                        <p><strong>生成者:</strong> ${generation.username}</p>
                        <p><strong>生成时间:</strong> ${generation.generated_at}</p>
                        <p><strong>卡片数量:</strong> ${generation.card_count}</p>
                        <p><strong>备注:</strong> ${generation.notes || '无'}</p>
                    </div>
                    <div class="export-buttons" style="margin: 20px 0;">
                        <button class="btn btn-success" onclick="exportCreditCards(${generationId}, 'csv')">导出CSV</button>
                        <button class="btn btn-success" onclick="exportCreditCards(${generationId}, 'excel')">导出Excel</button>
                    </div>
                    <div class="table-container">
                        <table class="admin-table">
                            <thead>
                                <tr>
                                    <th>卡片ID</th>
                                    <th>持卡人姓名</th>
                                    <th>有效期</th>
                                    <th>卡号</th>
                                    <th>安全码</th>
                                    <th>状态</th>
                                    <th>充值次数</th>
                                    <th>创建时间</th>
                                    <th>操作</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${cardsHtml}
                            </tbody>
                        </table>
                    </div>
                `;

        document.getElementById('creditCardGenerationDetailModal').classList.add('is-open');
      } else {
        showResultModal('加载失败', data.message, false);
      }
    })
    .catch(error => {
      console.error('Error:', error);
      showResultModal('加载失败', '网络错误，请重试', false);
    });
}

function closeCreditCardGenerationDetailModal() {
  document.getElementById('creditCardGenerationDetailModal').classList.remove('is-open');
}

function exportCreditCards(generationId, format) {
  const url = `/api/admin/credit-card-generations/${generationId}/export?format=${format}`;
  const link = document.createElement('a');
  link.href = url;
  link.download = `credit_cards_${generationId}.${format === 'excel' ? 'xlsx' : 'csv'}`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  closeCreditCardGenerationDetailModal();
  showResultModal('导出成功', '文件已开始下载');
}

function loadNotices() {
  fetch('/api/admin/notices')
    .then(response => response.json())
    .then(data => {
      const tbody = document.querySelector('#noticeTable tbody');
      tbody.innerHTML = '';

      data.notices.forEach(notice => {
        const tr = document.createElement('tr');

        tr.innerHTML = `
                    <td data-label="公告ID">${notice.id}</td>
                    <td data-label="标题">${notice.title}</td>
                    <td data-label="内容">${notice.content.substring(0, 50)}${notice.content.length > 50 ? '...' : ''}</td>
                    <td data-label="发布用户">${notice.username}</td>
                    <td data-label="创建时间">${notice.created_at}</td>
                    <td data-label="操作">
                        <button class="btn btn-danger" onclick="deleteNotice(${notice.id})">删除</button>
                    </td>
                `;
        tbody.appendChild(tr);
      });
    })
    .catch(error => console.error('Error:', error));
}

function showCreateNoticeModal() {
  document.getElementById('noticeTitle').value = '';
  document.getElementById('noticeContent').value = '';
  document.getElementById('createNoticeModal').classList.add('is-open');
}

function closeCreateNoticeModal() {
  document.getElementById('createNoticeModal').classList.remove('is-open');
}

function createNotice() {
  const title = document.getElementById('noticeTitle').value.trim();
  const content = document.getElementById('noticeContent').value.trim();

  if (!title || !content) {
    showResultModal('创建失败', '标题和内容不能为空', false);
    return;
  }

  fetch('/api/admin/notices', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        title: title,
        content: content
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        showResultModal('创建成功', '公告创建成功');
        closeCreateNoticeModal();
        loadNotices();
      } else {
        showResultModal('创建失败', data.error || '创建失败', false);
      }
    })
    .catch(error => {
      console.error('Error:', error);
      showResultModal('创建失败', '网络错误，请重试', false);
    });
}

function deleteNotice(noticeId) {
  showConfirmModal(
    '确认删除',
    '确定要删除此公告吗？',
    function() {
      fetch('/api/admin/notices/' + noticeId, {
          method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            showResultModal('删除成功', '公告删除成功');
            loadNotices();
          } else {
            showResultModal('删除失败', data.error || '删除失败', false);
          }
        })
        .catch(error => {
          console.error('Error:', error);
          showResultModal('删除失败', '网络错误，请重试', false);
        });
    }
  );
}