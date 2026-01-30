// 账号安全页面逻辑
(function() {
  'use strict';

  // 获取DOM元素
  const btnReal = document.getElementById('btnReal');
  const btnPayPwd = document.getElementById('btnPayPwd');
  const btnLoginPwd = document.getElementById('btnLoginPwd');
  const btnBindEmail = document.getElementById('btnBindEmail');

  // 页面加载时获取用户安全状态
  async function loadUserSecurityStatus() {
    try {
      const response = await fetch('/api/user/security', {
        credentials: 'include'
      });
      const data = await response.json();

      if (data.success) {
        updateUIStatus(data);
      }
    } catch (error) {
    }
  }

  // 根据用户状态更新UI
  function updateUIStatus(status) {
    // 实名认证按钮始终显示"實名認證"
    // 状态检查在点击时进行

    // 邮箱按钮始终显示"綁定郵箱"
    // 状态检查在点击时进行

    // 交易密码状态 - 即使已设置也要显示按钮，不显示"已设置"文本
    // if (status.has_pay_password) {
    //     btnPayPwd.textContent = '已設置交易密碼';
    //     btnPayPwd.disabled = true;
    //     btnPayPwd.style.opacity = '0.6';
    // }
  }

  // 创建模态框
  function createModal(title, content) {
    const modal = document.createElement('div');
    modal.className = 'modal-mask';
    modal.innerHTML = `
            <div class="modal">
                <div class="hdr">${title}</div>
                <div class="body">${content}</div>
            </div>
        `;
    document.body.appendChild(modal);
    return modal;
  }

  // 关闭模态框
  function closeModal(modal) {
    if (modal && modal.parentNode) {
      modal.parentNode.removeChild(modal);
    }
  }

  // 显示消息
  function showMessage(message, isSuccess = true) {
    // 简单的消息显示，可以后续优化
    alert(message);
  }

  // 实名认证
  btnReal.addEventListener('click', async function() {
    // 先获取当前用户状态，检查是否已实名认证
    try {
      const response = await fetch('/api/user/security', {
        credentials: 'include'
      });
      const data = await response.json();

      let content;
      if (data.success && data.verified) {
        // 已实名认证，显示信息展示框
        // 隐藏身份证号中间部分
        const maskedIdNumber = data.id_number ? data.id_number.substring(0, 6) +
          '********' + data.id_number.substring(14) : '';
        content = `
                    <div style="display: grid; gap: 12px;">
                        <div style="font-size: 14px; color: #cfe7ff;">實名認證信息：</div>
                        <div style="display: grid; gap: 8px;">
                            <div style="padding: 12px; background: rgba(255,255,255,.08); border-radius: 8px; color: #e6f0ff;">
                                <div style="font-size: 12px; color: #cfe7ff; margin-bottom: 4px;">真實姓名</div>
                                <div style="font-size: 16px;">${data.real_name || '未設置'}</div>
                            </div>
                            <div style="padding: 12px; background: rgba(255,255,255,.08); border-radius: 8px; color: #e6f0ff;">
                                <div style="font-size: 12px; color: #cfe7ff; margin-bottom: 4px;">身份證號</div>
                                <div style="font-size: 16px;">${maskedIdNumber}</div>
                            </div>
                            <div style="padding: 12px; background: rgba(255,255,255,.08); border-radius: 8px; color: #e6f0ff;">
                                <div style="font-size: 12px; color: #cfe7ff; margin-bottom: 4px;">手機號</div>
                                <div style="font-size: 16px;">${data.phone || '未設置'}</div>
                            </div>
                        </div>
                        <div style="font-size: 14px; color: #cfe7ff;">身份證照片：</div>
                        <div class="upload-grid">
                            <div style="display: grid; justify-items: center; gap: 8px; padding: 12px; background: rgba(255,255,255,.08); border-radius: 8px;">
                                <div style="font-size: 12px; color: #cfe7ff;">身份证正面</div>
                                ${data.id_front_image ? `
                                <img src="${data.id_front_image}" style="max-width: 100%; max-height: 120px; border-radius: 8px;" alt="身份证正面">
                                ` : `
                                <div style="width: 100%; height: 60px; background: rgba(255,255,255,.05); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #cfe7ff; font-size: 12px;">图片加载中或未找到</div>
                                `}
                            </div>
                            <div style="display: grid; justify-items: center; gap: 8px; padding: 12px; background: rgba(255,255,255,.08); border-radius: 8px;">
                                <div style="font-size: 12px; color: #cfe7ff;">身份证反面</div>
                                ${data.id_back_image ? `
                                <img src="${data.id_back_image}" style="max-width: 100%; max-height: 120px; border-radius: 8px;" alt="身份证反面">
                                ` : `
                                <div style="width: 100%; height: 60px; background: rgba(255,255,255,.05); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #cfe7ff; font-size: 12px;">图片加载中或未找到</div>
                                `}
                            </div>
                        </div>
                        <div class="actions">
                            <button class="btn secondary" onclick="this.closest('.modal-mask').remove()">關閉</button>
                            <button class="btn primary">已認證</button>
                        </div>
                    </div>
                `;
      } else {
        // 未实名认证，显示认证界面
        content = `
                    <div style="display: grid; gap: 12px;">
                        <input type="text" class="input" placeholder="請輸入真實姓名" id="realNameInput">
                        <input type="text" class="input" placeholder="請輸入身份證號" id="idNumberInput">
                        <input type="tel" class="input" placeholder="請輸入手機號" id="phoneInput">
                        <div style="font-size: 14px; color: #cfe7ff; margin-bottom: 8px;">請上傳身份證正反面照片：</div>
                        <div class="upload-grid">
                            <div class="upload-tile" id="frontUpload">
                                <div class="icon">
                                    <svg viewBox="0 0 24 24" width="32" height="32" fill="currentColor">
                                        <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
                                    </svg>
                                </div>
                                <div class="label">身份证正面</div>
                                <input type="file" id="idFrontInput" accept="image/*" style="display: none;">
                            </div>
                            <div class="upload-tile" id="backUpload">
                                <div class="icon">
                                    <svg viewBox="0 0 24 24" width="32" height="32" fill="currentColor">
                                        <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
                                    </svg>
                                </div>
                                <div class="label">身份证反面</div>
                                <input type="file" id="idBackInput" accept="image/*" style="display: none;">
                            </div>
                        </div>
                        <div class="actions">
                            <button class="btn secondary" onclick="this.closest('.modal-mask').remove()">取消</button>
                            <button class="btn primary" id="confirmVerify">确认</button>
                        </div>
                    </div>
                `;
      }

      const modal = createModal('实名认证', content);

      // 只有在未实名认证的情况下才添加文件上传和确认事件
      if (!data.success || !data.verified) {
        // 文件上传处理
        const frontUpload = document.getElementById('frontUpload');
        const backUpload = document.getElementById('backUpload');
        const idFrontInput = document.getElementById('idFrontInput');
        const idBackInput = document.getElementById('idBackInput');

        frontUpload.addEventListener('click', () => idFrontInput.click());
        backUpload.addEventListener('click', () => idBackInput.click());

        // 文件选择事件
        idFrontInput.addEventListener('change', function(e) {
          if (e.target.files[0]) {
            frontUpload.classList.add('selected');
            frontUpload.querySelector('.label').textContent = '已选择文件';
          }
        });

        idBackInput.addEventListener('change', function(e) {
          if (e.target.files[0]) {
            backUpload.classList.add('selected');
            backUpload.querySelector('.label').textContent = '已选择文件';
          }
        });

        document.getElementById('confirmVerify').addEventListener('click',
    async function() {
          const realName = document.getElementById('realNameInput').value.trim();
          const idNumber = document.getElementById('idNumberInput').value.trim();
          const phone = document.getElementById('phoneInput').value.trim();
          const idFrontFile = idFrontInput.files[0];
          const idBackFile = idBackInput.files[0];

          if (!realName || !idNumber || !phone) {
            showMessage('请填写完整信息', false);
            return;
          }

          if (!idFrontFile || !idBackFile) {
            showMessage('请上传身份证正反面照片', false);
            return;
          }

          // 创建FormData
          const formData = new FormData();
          formData.append('real_name', realName);
          formData.append('id_number', idNumber);
          formData.append('phone', phone);
          formData.append('id_front', idFrontFile);
          formData.append('id_back', idBackFile);

          try {
            const response = await fetch('/api/user/security/verify', {
              method: 'POST',
              body: formData,
              credentials: 'include'
            });

            const result = await response.json();
            if (result.success) {
              showMessage(result.message);
              closeModal(modal);
              // 刷新页面状态
              loadUserSecurityStatus();
            } else {
              showMessage(result.message, false);
            }
          } catch (error) {
            showMessage('网络错误，请重试', false);
          }
        });
      }

    } catch (error) {
      showMessage('获取用户信息失败', false);
    }
  });

  // 创建虚拟键盘
  function createKeypad(onComplete, onCancel) {
    const keypad = document.createElement('div');
    keypad.className = 'keypad-mask';
    keypad.innerHTML = `
            <div class="keypad">
                <div class="kp-title">請輸入交易密碼</div>
                <div class="kp-display" id="passwordDots">
                    ${Array(6).fill(0).map(() => '<div class="kp-dot"></div>').join('')}
                </div>
                <div class="kp-grid">
                    ${[1,2,3,4,5,6,7,8,9].map(num => `<button class="kp-key" data-value="${num}">${num}</button>`).join('')}
                    <div></div>
                    <button class="kp-key" data-value="0">0</button>
                    <button class="kp-key kp-del" data-value="del">⌫</button>
                </div>
                <div class="kp-actions">
                    <button class="kp-key" id="kpCancel">取消</button>
                    <button class="kp-key kp-primary" id="kpConfirm">确认</button>
                </div>
            </div>
        `;
    document.body.appendChild(keypad);

    let password = '';
    const dots = keypad.querySelectorAll('.kp-dot');

    // 键盘按键事件
    keypad.querySelectorAll('.kp-key').forEach(key => {
      key.addEventListener('click', function() {
        const value = this.dataset.value;
        if (value >= '0' && value <= '9' && password.length < 6) {
          password += value;
          updateDots();
        } else if (value === 'del' && password.length > 0) {
          password = password.slice(0, -1);
          updateDots();
        }
      });
    });

    function updateDots() {
      dots.forEach((dot, index) => {
        dot.classList.toggle('filled', index < password.length);
      });
    }

    keypad.querySelector('#kpCancel').addEventListener('click', function() {
      document.body.removeChild(keypad);
      onCancel && onCancel();
    });

    keypad.querySelector('#kpConfirm').addEventListener('click', function() {
      document.body.removeChild(keypad);
      onComplete && onComplete(password);
    });

    return keypad;
  }

  // 显示软键盘
  function showKeypad(title, onDone) {
    let ov = document.createElement('div');
    ov.className = 'keypad-mask';
    ov.innerHTML = (
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
    ov.addEventListener('click', (e) => {
      if (e.target === ov) {
        ov.remove();
      }
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

  // 交易密码
  btnPayPwd.addEventListener('click', async function() {
    // 先获取当前用户状态，检查是否已设置交易密码
    try {
      const response = await fetch('/api/user/security', {
        credentials: 'include'
      });
      const data = await response.json();

      let content;
      let apiUrl;
      let buttonText;

      if (data.success && data.has_pay_password) {
        // 已设置交易密码，显示修改界面（不需要输入当前密码）
        content = `
                    <div style="display: grid; gap: 12px;">
                        <input type="password" class="input" placeholder="請輸入新交易密碼" id="newPayPwdInput" readonly style="cursor: pointer;">
                        <input type="password" class="input" placeholder="請確認新交易密碼" id="confirmNewPayPwdInput" readonly style="cursor: pointer;">
                        <div class="actions">
                            <button class="btn secondary" onclick="this.closest('.modal-mask').remove()">取消</button>
                            <button class="btn primary" id="confirmPayPwd">確認修改</button>
                        </div>
                    </div>
                `;
        apiUrl = '/api/user/security/change-pay-password';
        buttonText = '確認修改';
      } else {
        // 未设置交易密码，显示设置界面
        content = `
                    <div style="display: grid; gap: 12px;">
                        <input type="password" class="input" placeholder="請輸入交易密碼" id="payPwdInput" readonly style="cursor: pointer;">
                        <input type="password" class="input" placeholder="請確認交易密碼" id="confirmPayPwdInput" readonly style="cursor: pointer;">
                        <div class="actions">
                            <button class="btn secondary" onclick="this.closest('.modal-mask').remove()">取消</button>
                            <button class="btn primary" id="confirmPayPwd">確認</button>
                        </div>
                    </div>
                `;
        apiUrl = '/api/user/security/pay-password';
        buttonText = '確認';
      }

      const modal = createModal('交易密碼', content);

      // 为密码输入框添加软键盘
      const newPayPwdInput = document.getElementById('newPayPwdInput');
      const confirmNewPayPwdInput = document.getElementById('confirmNewPayPwdInput');
      const payPwdInput = document.getElementById('payPwdInput');
      const confirmPayPwdInput = document.getElementById('confirmPayPwdInput');

      if (newPayPwdInput) {
        newPayPwdInput.addEventListener('click', () => {
          showKeypad('請輸入新交易密碼', v => {
            newPayPwdInput.value = v;
          });
        });
      }

      if (confirmNewPayPwdInput) {
        confirmNewPayPwdInput.addEventListener('click', () => {
          showKeypad('請確認新交易密碼', v => {
            confirmNewPayPwdInput.value = v;
          });
        });
      }

      if (payPwdInput) {
        payPwdInput.addEventListener('click', () => {
          showKeypad('請輸入交易密碼', v => {
            payPwdInput.value = v;
          });
        });
      }

      if (confirmPayPwdInput) {
        confirmPayPwdInput.addEventListener('click', () => {
          showKeypad('請確認交易密碼', v => {
            confirmPayPwdInput.value = v;
          });
        });
      }

      document.getElementById('confirmPayPwd').addEventListener('click', async function() {
        let requestData;

        if (data.success && data.has_pay_password) {
          // 修改模式（不需要验证当前密码）
          const newPassword = document.getElementById('newPayPwdInput').value;
          const confirmPassword = document.getElementById('confirmNewPayPwdInput')
            .value;

          if (!newPassword || !confirmPassword) {
            showMessage('請填寫完整信息', false);
            return;
          }

          if (newPassword !== confirmPassword) {
            showMessage('新密碼和確認密碼不一致', false);
            return;
          }

          if (!/^\d{6}$/.test(newPassword)) {
            showMessage('交易密碼必須為6位數字', false);
            return;
          }

          requestData = {
            new_password: newPassword,
            confirm_password: confirmPassword
          };
        } else {
          // 设置模式
          const password = document.getElementById('payPwdInput').value;
          const confirmPassword = document.getElementById('confirmPayPwdInput').value;

          if (!password || !confirmPassword) {
            showMessage('請填寫完整信息', false);
            return;
          }

          if (password !== confirmPassword) {
            showMessage('兩次密碼輸入不一致', false);
            return;
          }

          if (!/^\d{6}$/.test(password)) {
            showMessage('交易密碼必須為6位數字', false);
            return;
          }

          requestData = {
            password: password,
            confirm_password: confirmPassword
          };
        }

        try {
          const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(requestData)
          });

          const result = await response.json();
          if (result.success) {
            showMessage(result.message);
            closeModal(modal);
            // 刷新页面状态
            loadUserSecurityStatus();
          } else {
            showMessage(result.message, false);
          }
        } catch (error) {
          showMessage('網絡錯誤，請重試', false);
        }
      });

    } catch (error) {
      showMessage('獲取用戶信息失敗', false);
    }
  });

  // 登录密码
  btnLoginPwd.addEventListener('click', function() {
    const content = `
            <div style="display: grid; gap: 12px;">
                <input type="password" class="input" placeholder="請輸入當前密碼" id="oldPwdInput">
                <input type="password" class="input" placeholder="請輸入新密碼" id="newPwdInput">
                <input type="password" class="input" placeholder="請確認新密碼" id="confirmNewPwdInput">
                <div class="actions">
                    <button class="btn secondary" onclick="this.closest('.modal-mask').remove()">取消</button>
                    <button class="btn primary" id="confirmChangePwd">確認</button>
                </div>
            </div>
        `;

    const modal = createModal('修改登入密碼', content);

    document.getElementById('confirmChangePwd').addEventListener('click', async function() {
      const oldPassword = document.getElementById('oldPwdInput').value;
      const newPassword = document.getElementById('newPwdInput').value;
      const confirmPassword = document.getElementById('confirmNewPwdInput').value;

      if (!oldPassword || !newPassword || !confirmPassword) {
        showMessage('请填写完整信息', false);
        return;
      }

      if (newPassword !== confirmPassword) {
        showMessage('新密码和确认密码不一致', false);
        return;
      }

      try {
        const response = await fetch('/api/user/security/password', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({
            old_password: oldPassword,
            new_password: newPassword,
            confirm_password: confirmPassword
          })
        });

        const result = await response.json();
        if (result.success) {
          showMessage('登录密码修改成功');
          closeModal(modal);
        } else {
          showMessage(result.message, false);
        }
      } catch (error) {
        showMessage('网络错误，请重试', false);
      }
    });
  });

  // 绑定邮箱
  btnBindEmail.addEventListener('click', async function() {
    // 先获取当前用户状态
    try {
      const response = await fetch('/api/user/security', {
        credentials: 'include'
      });
      const data = await response.json();

      let content;
      if (data.success && data.email) {
        // 已绑定邮箱，显示当前邮箱和两个按钮
        content = `
                    <div style="display: grid; gap: 12px;">
                        <div style="font-size: 14px; color: #cfe7ff;">當前綁定郵箱：</div>
                        <div style="padding: 12px; background: rgba(255,255,255,.08); border-radius: 8px; color: #e6f0ff; font-size: 16px; text-align: center;">${data.email}</div>
                        <div class="actions">
                            <button class="btn secondary" onclick="this.closest('.modal-mask').remove()">關閉</button>
                            <button class="btn primary">已綁定</button>
                        </div>
                    </div>
                `;
      } else {
        // 未绑定邮箱，显示绑定界面
        content = `
                    <div style="display: grid; gap: 12px;">
                        <input type="email" class="input" placeholder="請輸入郵箱地址" id="emailInput">
                        <div class="actions">
                            <button class="btn secondary" onclick="this.closest('.modal-mask').remove()">取消</button>
                            <button class="btn primary" id="confirmBindEmail">確認</button>
                        </div>
                    </div>
                `;
      }

      const modal = createModal('綁定郵箱', content);

      // 只有在未绑定邮箱的情况下才添加确认按钮事件
      if (!data.success || !data.email) {
        document.getElementById('confirmBindEmail').addEventListener('click',
        async function() {
            const email = document.getElementById('emailInput').value.trim();

            if (!email) {
              showMessage('请输入邮箱地址', false);
              return;
            }

            if (!email.includes('@') || !email.includes('.')) {
              showMessage('邮箱格式不正确', false);
              return;
            }

            try {
              const response = await fetch('/api/user/security/email', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                  email: email
                })
              });

              const result = await response.json();
              if (result.success) {
                showMessage('邮箱绑定成功');
                closeModal(modal);
                // 刷新页面状态
                loadUserSecurityStatus();
              } else {
                showMessage(result.message, false);
              }
            } catch (error) {
              showMessage('网络错误，请重试', false);
            }
          });
      }

    } catch (error) {
      showMessage('网络连接失败，请检查网络连接', false);
    }
  });

  // 页面加载初始化
  document.addEventListener('DOMContentLoaded', function() {
    loadUserSecurityStatus();
  });

})();