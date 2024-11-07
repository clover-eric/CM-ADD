async function generateApiKey() {
    try {
        const response = await fetch('/api/generate_key', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            location.reload();  // 刷新页面显示新密钥
        } else {
            showAlert(data.message || '生成密钥失败', 'danger');
        }
    } catch (error) {
        showAlert('服务器错误，请稍后重试', 'danger');
    }
}

function copyApiKey() {
    const apiKeyInput = document.getElementById('apiKey');
    apiKeyInput.select();
    document.execCommand('copy');
    
    const button = event.target.closest('button');
    const originalHtml = button.innerHTML;
    button.innerHTML = '<i class="fas fa-check"></i>';
    button.disabled = true;
    
    setTimeout(() => {
        button.innerHTML = originalHtml;
        button.disabled = false;
    }, 2000);
}

// 代码高亮
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightBlock(block);
    });
}); 