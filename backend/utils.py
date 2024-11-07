import os
import magic
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

def allowed_file(file):
    """检查文件类型是否允许"""
    try:
        mime = magic.Magic(mime=True)
        file_type = mime.from_buffer(file.read())
        file.seek(0)  # 重置文件指针
        
        ALLOWED_MIMES = [
            'text/plain',
            'text/csv',
            'application/vnd.ms-excel',
            'application/pdf'
        ]
        
        return file_type in ALLOWED_MIMES
    except Exception as e:
        print(f"文件类型检查错误: {str(e)}")
        return False

def format_file_size(size):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"

def generate_unique_filename(original_filename):
    """生成基于时间戳的唯一文件名"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}.{ext}" if ext else f"{timestamp}_{unique_id}"

def get_file_type_icon(filename):
    """根据文件类型返回对应的Font Awesome图标类名"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    icons = {
        'txt': 'fa-file-alt',
        'csv': 'fa-file-csv',
        'pdf': 'fa-file-pdf',
        'xls': 'fa-file-excel',
        'xlsx': 'fa-file-excel'
    }
    return icons.get(ext, 'fa-file')

def get_safe_filename(filename):
    """获取安全的文件名"""
    name = secure_filename(filename)
    # 确保文件名不为空
    if not name:
        name = 'unnamed_file'
    return name