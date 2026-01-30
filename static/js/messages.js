function loadMessages() {
  fetch('/api/messages')
    .then(response => response.json())
    .then(data => {
      const tbody = document.getElementById('messagesTableBody');
      if (!tbody) return;

      if (!data.success || !data.messages || data.messages.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="empty-state">暫無消息</td></tr>';
        return;
      }

      tbody.innerHTML = data.messages.map(message => `
        <tr data-id="${message.id}" class="${message.is_read ? 'read' : 'unread'}">
          <td class="title">${message.title}</td>
          <td class="date">${formatDate(message.created_at)}</td>
          <td class="status">
            <span class="status-badge ${message.is_read ? 'read' : 'unread'}">
              ${message.is_read ? '已读' : '未读'}
            </span>
          </td>
          <td class="actions">
            <button class="view-btn" onclick="viewMessage(${message.id})">查看</button>
          </td>
        </tr>
      `).join('');
    })
    .catch(error => {
      console.error('加载消息失败:', error);
      const table = document.getElementById('messagesTable');
      table.innerHTML = '<div class="no-messages">加载失败，请稍后重试</div>';
    });
}

function formatDate(dateString) {
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${year}-${month}-${day} ${hours}:${minutes}`;
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
        showNotification(data.error || '获取消息详情失败', 'error');
      }
    })
    .catch(error => {
      console.error('查看消息失败:', error);
      showNotification('查看消息失败，请稍后重试', 'error');
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
        loadMessages();
      }
    })
    .catch(error => {
      console.error('标记已读失败:', error);
    });
}

function showMessageDetail(message) {
  const modal = document.createElement('div');
  modal.className = 'message-modal';
  modal.innerHTML = `
    <div class="message-modal-mask"></div>
    <div class="message-modal-content">
      <div class="message-modal-header">
        <h3>${message.title}</h3>
        <button class="close-btn" onclick="this.closest('.message-modal').remove()">&times;</button>
      </div>
      <div class="message-modal-body">
        <div class="message-time">${formatDate(message.created_at)}</div>
        <div class="message-content">${message.content}</div>
      </div>
      <div class="message-modal-footer">
        <button class="btn secondary" onclick="this.closest('.message-modal').remove()">关闭</button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);
}

function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.className = `notification ${type}`;
  notification.textContent = message;

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.remove();
  }, 3000);
}

document.addEventListener('DOMContentLoaded', loadMessages);
