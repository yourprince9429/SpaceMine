// SpaceMine 注册页面JavaScript（完全参考原始网站逻辑）

const statusDiv = document.getElementById('status');

// 协议模态框功能
const agreementModal = document.getElementById('agreementModalRegister');
const modalTitle = document.getElementById('modalTitleRegister');
const modalContent = document.getElementById('modalContentRegister');
const modalClose = document.getElementById('modalCloseRegister');

// 用户协议内容（完全匹配原始网站）
const userAgreement = `歡迎使用本服務。您在使用前需認真閱讀並同意本用戶協議：
1. 帳戶與安全：請妥善保管帳號和密碼，不得轉讓或共享。
2. 合理使用：不得利用本服務從事違法違規行為或破壞系統安全的活動。
3. 內容與隱私：您提交的內容應合法合規，平台有權依據法律法規進行處理。
4. 服務變更：平台可根據業務需要調整功能，並提前公告重要變更。
5. 責任限制：在法律允許範圍內，平台不對因不可抗力導致的損失負責。
6. 爭議解決：爭議應友好協商解決，協商不成的，提交平台所在地法院處理。`;

// 隐私政策内容（完全匹配原始网站）
const privacyPolicy = `我們重視您的隱私與數據安全：
1. 收集資訊：用於註冊、登入、風控與服務提供的必要資訊。
2. 使用目的：提升服務品質、保障帳戶安全、履行法律義務。
3. 資訊共享：除法律規定或經您同意外，不與第三方共享可識別資訊。
4. 安全措施：採取合理的技術與管理措施保護您的數據安全。
5. 權利保障：您可依法查詢、更正或刪除個人資訊並撤回授權。
6. 變更說明：政策調整將以公告形式告知並在生效前提示。`;

// 显示协议模态框
function showAgreement(type) {
  if (type === 'userAgreement') {
    modalTitle.textContent = '用戶協議';
    modalContent.textContent = userAgreement;
  } else if (type === 'privacyPolicy') {
    modalTitle.textContent = '隱私政策';
    modalContent.textContent = privacyPolicy;
  }
  agreementModal.classList.add('is-open');
}

// 隐藏协议模态框
function hideAgreement() {
  agreementModal.classList.remove('is-open');
}

// 注册按钮点击处理
const registerBtn = document.getElementById('btnRegister');
if (registerBtn) {
  registerBtn.addEventListener('click', function() {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();
    const confirm = document.getElementById('confirm').value.trim();
    const paypwd = document.getElementById('paypwd').value.trim();
    const invite = document.getElementById('invite').value.trim();
    const agree = document.getElementById('agreeRegister').checked;

    if (!invite) {
      statusDiv.textContent = '請輸入邀請碼';
      return;
    }
    if (!username || !password || !paypwd) {
      statusDiv.textContent = '請輸入所有必填字段';
      return;
    }
    if (password !== confirm) {
      statusDiv.textContent = '兩次輸入的密碼不一致';
      return;
    }
    if (password.length < 6) {
      statusDiv.textContent = '密碼至少6位';
      return;
    }
    if (paypwd.length !== 6 || !/^\d{6}$/.test(paypwd)) {
      statusDiv.textContent = '支付密碼必須是6位數字';
      return;
    }
    if (!agree) {
      statusDiv.textContent = '請先閱讀並同意用戶協議與隱私政策';
      return;
    }

    statusDiv.textContent = '註冊中...';

    // 发送注册请求
    fetch('/api/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username,
          password: password,
          paypwd: paypwd,
          invite_code: invite
        })
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          statusDiv.textContent = '註冊成功，跳轉登入…';
          setTimeout(() => {
            window.location.href = '/';
          }, 1000);
        } else {
          statusDiv.textContent = data.message;
        }
      })
      .catch(error => {
        console.error('注册错误:', error);
        statusDiv.textContent = '註冊失敗，請重試';
      });
  });
}

// URL参数处理邀请码（参考原始网站逻辑）
(function() {
  const params = new URLSearchParams(window.location.search);
  const inviteCode = params.get('invite_code');
  if (inviteCode) {
    const inviteInput = document.getElementById('invite');
    inviteInput.value = inviteCode;
    inviteInput.readOnly = true;
    inviteInput.style.opacity = '0.9';
    inviteInput.title = '邀請碼已鎖定';
  }
})();

// 协议链接事件监听器
document.getElementById('userAgreementLinkRegister').addEventListener('click', function(e) {
  e.preventDefault();
  showAgreement('userAgreement');
});

document.getElementById('privacyPolicyLinkRegister').addEventListener('click', function(e) {
  e.preventDefault();
  showAgreement('privacyPolicy');
});

modalClose.addEventListener('click', hideAgreement);

// 点击模态框背景关闭
agreementModal.addEventListener('click', function(e) {
  if (e.target === agreementModal) {
    hideAgreement();
  }
});

// 按ESC键关闭模态框
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    hideAgreement();
  }
});