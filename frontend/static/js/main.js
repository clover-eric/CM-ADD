// 文件上传预览
function handleFileSelect(evt) {
    const files = evt.target.files;
    const output = document.getElementById('file-list');
    if (!output) return;
    
    output.innerHTML = '';

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const div = document.createElement('div');
        div.className = 'file-item';
        div.innerHTML = `
            <i class="fas fa-file file-icon"></i>
            <div class="file-info">
                <div class="file-name">${file.name}</div>
                <div class="file-size">${formatFileSize(file.size)}</div>
            </div>
        `;
        output.appendChild(div);
    }
}

// 复制链接功能
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showAlert('链接已复制到剪贴板', 'success');
    }).catch(err => {
        showAlert('复制失败，请手动复制', 'danger');
        console.error('复制失败:', err);
    });
}

// 通用提示框
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.alert-container') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => alertDiv.remove(), 150);
    }, 3000);
}

// 文件清空确认
function confirmClearCabinet() {
    if (confirm('确定要清空文件柜吗？此操作不可恢复！')) {
        fetch('/clear-cabinet', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.reload();
            } else {
                showAlert(data.message || '操作失败', 'danger');
            }
        })
        .catch(error => {
            showAlert('服务器错误，请重试', 'danger');
            console.error('Error:', error);
        });
    }
}

// 初始化所有组件
document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(el => new bootstrap.Tooltip(el));
    
    // 初始化文件上传监听
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }
    
    // 初始化拖放区域
    const dropZone = document.getElementById('drop-zone');
    if (dropZone) {
        dropZone.addEventListener('dragover', handleDragOver);
        dropZone.addEventListener('drop', handleDrop);
    }
    
    // 自动关闭现有警告提示
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 150);
        }, 3000);
    });
});

// 文件大小格式化
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 文件拖放上传
function handleDragOver(evt) {
    evt.stopPropagation();
    evt.preventDefault();
    evt.dataTransfer.dropEffect = 'copy';
}

function handleDrop(evt) {
    evt.stopPropagation();
    evt.preventDefault();

    const files = evt.dataTransfer.files;
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.files = files;
        const event = new Event('change');
        fileInput.dispatchEvent(event);
    }
}

// 自动关闭警告提示
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 150);
        }, 3000);
    });
}); 