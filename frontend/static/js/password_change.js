document.addEventListener('DOMContentLoaded', function() {
    // 检查是否需要显示修改密码弹窗
    if (document.body.dataset.firstLogin === 'true') {
        const modal = new bootstrap.Modal(document.getElementById('changePasswordModal'));
        modal.show();
    }

    // 密码强度检查
    const passwordInput = document.getElementById('new_password');
    const strengthIndicator = document.querySelector('.password-strength');
    
    passwordInput.addEventListener('input', function() {
        const password = this.value;
        let strength = 0;
        
        if (password.length >= 8) strength++;
        if (password.match(/[a-z]/) && password.match(/[A-Z]/)) strength++;
        if (password.match(/\d/)) strength++;
        if (password.match(/[^a-zA-Z\d]/)) strength++;
        
        strengthIndicator.className = 'password-strength';
        if (strength > 3) strengthIndicator.classList.add('strength-strong');
        else if (strength > 2) strengthIndicator.classList.add('strength-medium');
        else strengthIndicator.classList.add('strength-weak');
    });

    // 表单提交处理
    document.getElementById('submitChangePassword').addEventListener('click', async function() {
        const form = document.getElementById('changePasswordForm');
        const formData = new FormData(form);

        if (formData.get('new_password') !== formData.get('confirm_password')) {
            showAlert('两次输入的密码不一致', 'danger');
            return;
        }

        try {
            const response = await fetch('/auth/change_default_password', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();
            
            if (response.ok) {
                showAlert('密码修改成功，即将跳转...', 'success');
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1500);
            } else {
                showAlert(data.message, 'danger');
            }
        } catch (error) {
            showAlert('服务器错误，请稍后重试', 'danger');
        }
    });

    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.querySelector('.modal-body').insertBefore(alertDiv, document.querySelector('form'));
        
        setTimeout(() => {
            alertDiv.remove();
        }, 3000);
    }
}); 