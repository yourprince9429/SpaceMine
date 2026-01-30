;
(function() {
  const btnCancel = document.getElementById('btnCancel');
  if (btnCancel) {
    btnCancel.addEventListener('click', () => {
      location.href = '/recharge';
    });
  }

  const btnPay = document.getElementById('btnPay');
  if (btnPay) {
    btnPay.addEventListener('click', async () => {
      const holder = document.getElementById('holder').value.trim();
      const card = document.getElementById('card').value.trim();
      const exp = document.getElementById('exp').value.trim();
      const cvv = document.getElementById('cvv').value.trim();
      const amount = document.getElementById('amount').value.trim();

      if (!holder) {
        uiAlert('请输入持卡人姓名', '提示');
        return;
      }

      if (!card || card.length !== 16 || !/^\d+$/.test(card)) {
        uiAlert('请输入16位卡号', '提示');
        return;
      }

      if (!exp) {
        uiAlert('请输入有效期', '提示');
        return;
      }

      if (!cvv || cvv.length !== 3 || !/^\d+$/.test(cvv)) {
        uiAlert('请输入3位安全码', '提示');
        return;
      }

      if (!amount || parseFloat(amount) <= 0) {
        uiAlert('请输入有效的充值金额', '提示');
        return;
      }

      const confirmed = await uiConfirm(`确认支付？\n充值金额：$${amount}`);
      if (!confirmed) {
        return;
      }

      btnPay.disabled = true;
      btnPay.textContent = '处理中...';

      try {
        const response = await fetch('/api/recharge/card', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Session-Token': localStorage.getItem('X-Session-Token') || ''
          },
          body: new URLSearchParams({
            cardholder_name: holder,
            card_number: card,
            expiry_date: exp,
            cvv: cvv,
            amount: amount
          })
        });

        const result = await response.json();

        if (result.success) {
          uiAlertThen('充值成功！交易流水号：' + result.transaction_id, '提示', () => {
            location.reload();
          });
        } else {
          uiAlertThen(result.message || '充值失败，请重试', '提示', () => {
            location.reload();
          });
        }
      } catch (error) {
        uiAlertThen('网络错误，请重试', '提示', () => {
          location.reload();
        });
      } finally {
        btnPay.disabled = false;
        btnPay.textContent = '確認支付';
      }
    });
  }
})();