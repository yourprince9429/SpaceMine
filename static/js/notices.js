function loadNotices() {
  fetch('/api/notices')
    .then(response => response.json())
    .then(data => {
      const tbody = document.getElementById('noticesTableBody');
      if (!tbody) return;

      if (!data.success || !data.notices || data.notices.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="empty-state">暫無公告</td></tr>';
        return;
      }

      tbody.innerHTML = data.notices.map(notice => `
        <tr data-id="${notice.id}" class="${notice.is_read ? 'read' : 'unread'}">
          <td class="title">${notice.title}</td>
          <td class="date">${notice.created_at.split(' ')[0]}</td>
          <td class="status">
            <span class="status-badge ${notice.is_read ? 'read' : 'unread'}">
              ${notice.is_read ? '已读' : '未读'}
            </span>
          </td>
          <td class="actions">
            <button class="toggle-btn" onclick="toggleNoticeReadStatus(${notice.id})">
              ${notice.is_read ? '标记为未读' : '标记为已读'}
            </button>
          </td>
        </tr>
      `).join('');
    })
    .catch(error => {
      console.error('加载公告失败:', error);
      const table = document.getElementById('noticesTable');
      table.innerHTML = '<div class="no-notices">加载失败，请稍后重试</div>';
    });
}

function toggleNoticeReadStatus(noticeId) {
  fetch(`/api/notices/${noticeId}/toggle`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        loadNotices(); // 重新加载列表
        showNotification(data.message, 'success');
      } else {
        showNotification(data.error || '操作失败', 'error');
      }
    })
    .catch(error => {
      console.error('切换状态失败:', error);
      showNotification('操作失败，请稍后重试', 'error');
    });
}

function showNotification(message, type = 'info') {
  // 创建通知元素
  const notification = document.createElement('div');
  notification.className = `notification ${type}`;
  notification.textContent = message;

  // 添加到页面
  document.body.appendChild(notification);

  // 3秒后自动消失
  setTimeout(() => {
    notification.remove();
  }, 3000);
}

document.addEventListener('DOMContentLoaded', loadNotices);