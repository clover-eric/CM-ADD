// 编辑用户
async function editUser(userId) {
    try {
        const response = await fetch(`/admin/user/${userId}`);
        const user = await response.json();
        
        document.getElementById('userId').value = user.id;
        document.getElementById('editUsername').value = user.username;
        document.getElementById('editEmail').value = user.email;
        document.getElementById('editIsActive').checked = user.is_active;
        
        const modal = new bootstrap.Modal(document.getElementById('editUserModal'));
        modal.show();
    } catch (error) {
        showAlert('获取用户信息失败', 'danger');
    }
}

// 更新用户信息
async function updateUser() {
    const userId = document.getElementById('userId').value;
    const data = {
        username: document.getElementById('editUsername').value,
        email: document.getElementById('editEmail').value,
        is_active: document.getElementById('editIsActive').checked
    };
    
    try {
        const response = await fetch(`/admin/user/${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        if (response.ok) {
            location.reload();
        } else {
            showAlert(result.message || '更新失败', 'danger');
        }
    } catch (error) {
        showAlert('服务器错误', 'danger');
    }
}

// 确认删除用户
function confirmDeleteUser(userId, username) {
    if (confirm(`确定要删除用户 "${username}" 吗？此操作不可撤销。`)) {
        deleteUser(userId);
    }
}

// 删除用户
async function deleteUser(userId) {
    try {
        const response = await fetch(`/admin/user/${userId}`, {
            method: 'DELETE',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        const result = await response.json();
        if (response.ok) {
            location.reload();
        } else {
            showAlert(result.message || '删除失败', 'danger');
        }
    } catch (error) {
        showAlert('服务器错误', 'danger');
    }
}

// 显示系统重置确认框
function confirmSystemReset() {
    const modal = new bootstrap.Modal(document.getElementById('resetConfirmModal'));
    modal.show();
}

// 执行系统重置
async function executeSystemReset() {
    const confirmInput = document.getElementById('resetConfirmInput').value;
    if (confirmInput !== 'RESET') {
        showAlert('请输入正确的确认文字', 'danger');
        return;
    }
    
    try {
        const response = await fetch('/admin/system/reset', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        const result = await response.json();
        if (response.ok) {
            showAlert('系统重置成功，即将跳转...', 'success');
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
        } else {
            showAlert(result.message || '重置失败', 'danger');
        }
    } catch (error) {
        showAlert('服务器错误', 'danger');
    }
} 