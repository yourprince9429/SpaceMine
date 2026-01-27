;
(function() {
  const btnCancel = document.getElementById('btnCancel');
  if (btnCancel) {
    btnCancel.addEventListener('click', () => {
      location.href = '/recharge';
    });
  }
  const btnSubmit = document.getElementById('btnSubmit');
  if (btnSubmit) {
    btnSubmit.addEventListener('click', async () => {
      // 获取表单数据
      const amount = document.getElementById('amount').value.trim();
      const voucher = document.getElementById('voucher').files[0];

      // 验证数据
      if (!amount) {
        uiAlert('请输入充值金额');
        return;
      }

      if (!voucher) {
        uiAlert('请上传充值凭证');
        return;
      }

      try {
        // 创建FormData
        const formData = new FormData();
        formData.append('amount', amount);
        formData.append('voucher', voucher);

        // 调用后端接口
        const response = await fetch('/api/recharge/usdt', {
          method: 'POST',
          headers: {
            'X-Session-Token': localStorage.getItem('X-Session-Token') || ''
          },
          body: formData,
          credentials: 'include'
        });

        const result = await response.json();

        if (result.success) {
          uiAlert(result.message, '提示', () => {
            location.href = '/recharge';
          });
        } else {
          uiAlert(result.message, '提示', () => {
            location.reload();
          });
        }
      } catch (error) {
        console.error('提交失败:', error);
        uiAlert('提交失败，请重试', '提示', () => {
          location.reload();
        });
      }
    });
  }
  const btnCopy = document.getElementById('btnCopy');
  if (btnCopy) {
    btnCopy.addEventListener('click', () => {
      const addrVal = document.getElementById('addrVal').textContent;
      navigator.clipboard.writeText(addrVal).then(() => {
        uiAlert('地址已复制', '提示');
      });
    });
  }
  const uploadBox = document.getElementById('uploadBox');
  const voucher = document.getElementById('voucher');
  const preview = document.getElementById('preview');
  const previewImg = document.getElementById('previewImg');
  const btnDelete = document.getElementById('btnDelete');
  const btnReupload = document.getElementById('btnReupload');

  if (uploadBox && voucher) {
    uploadBox.addEventListener('click', () => {
      voucher.click();
    });
    voucher.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          previewImg.src = e.target.result;
          preview.style.display = 'block';
          uploadBox.style.display = 'none'; // 隐藏上传框
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // 删除按钮
  if (btnDelete) {
    btnDelete.addEventListener('click', () => {
      preview.style.display = 'none';
      uploadBox.style.display = 'grid'; // 显示上传框
      voucher.value = ''; // 清空文件选择
    });
  }

  // 重传按钮
  if (btnReupload) {
    btnReupload.addEventListener('click', () => {
      voucher.click();
    });
  }
})();