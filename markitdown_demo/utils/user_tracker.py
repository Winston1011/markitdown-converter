import json
import time
from pathlib import Path
from datetime import datetime
from markitdown_demo.config.settings import VALID_CONVERT_CNT, VALID_CHAT_CNT

class UserTracker:
    def __init__(self, data_file="user_ip.json"):
        self.data_file = Path(data_file)
        self._ensure_file_exists()
        self.data = self._load_data()
    
    def can_convert(self, ip):
        """检查用户是否还可以进行转换"""
        user_data = self._get_user_data(ip)
        current_count = user_data.get("convert_count", 0)
        remaining = VALID_CONVERT_CNT - current_count
        return remaining > 0, remaining
    
    def can_chat(self, ip):
        """检查用户是否还可以进行对话"""
        user_data = self._get_user_data(ip)
        current_count = user_data.get("chat_count", 0)
        remaining = VALID_CHAT_CNT - current_count
        return remaining > 0, remaining
    
    def _ensure_file_exists(self):
        """确保数据文件存在"""
        if not self.data_file.exists():
            self.data_file.write_text("{}")
    
    def _load_data(self):
        """加载用户数据"""
        try:
            if self.data_file.exists():
                content = self.data_file.read_text()
                if content.strip():
                    return json.loads(content)
            return {}
        except Exception as e:
            print(f"加载用户数据失败: {str(e)}")
            return {}
    
    def _save_data(self):
        """保存用户数据"""
        try:
            self.data_file.write_text(json.dumps(self.data, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"保存用户数据失败: {str(e)}")
    
    def _get_user_data(self, ip):
        """获取用户数据，如果不存在则初始化"""
        if not ip or ip == 'unknown':
            ip = 'unknown'
        if ip not in self.data:
            self.data[ip] = {
                "chat_count": 0,
                "file_count": 0,
                "total_file_size": 0,
                "first_visit": datetime.now().isoformat(),
                "last_visit": datetime.now().isoformat(),
                "visit_count": 0,
                "convert_count": 0
            }
        return self.data[ip]
    
    def record_visit(self, ip):
        """记录用户访问"""
        user_data = self._get_user_data(ip)
        user_data["visit_count"] += 1
        user_data["last_visit"] = datetime.now().isoformat()
        self._save_data()
    
    def record_chat(self, ip):
        """记录用户对话次数"""
        can_chat, remaining = self.can_chat(ip)
        if can_chat:
            user_data = self._get_user_data(ip)
            user_data["chat_count"] += 1
            self._save_data()
            return True, remaining - 1
        return False, 0
    
    def record_convert(self, ip, count=1):
        """记录文件转换次数"""
        try:
            if not ip or ip == 'unknown':
                ip = 'unknown'
            can_convert, remaining = self.can_convert(ip)
            if not can_convert:
                return False, 0
            
            user_data = self._get_user_data(ip)
            if "convert_count" not in user_data:
                user_data["convert_count"] = 0
            user_data["convert_count"] += count
            self._save_data()
            print(f"记录转换次数成功: IP={ip}, count={count}, 当前总次数={user_data['convert_count']}")
            return True, remaining - count
        except Exception as e:
            print(f"记录转换次数失败: {str(e)}")
            return False, 0
    
    def record_file_upload(self, ip, file_size):
        """记录用户文件上传"""
        user_data = self._get_user_data(ip)
        user_data["file_count"] += 1
        user_data["total_file_size"] += file_size
        self._save_data()
    
    def get_user_stats(self, ip):
        """获取用户统计信息"""
        try:
            user_data = self._get_user_data(ip)
            if "convert_count" not in user_data:
                user_data["convert_count"] = 0
            return user_data
        except Exception as e:
            print(f"获取用户统计信息失败: {str(e)}")
            return {
                "chat_count": 0,
                "file_count": 0,
                "total_file_size": 0,
                "first_visit": "",
                "last_visit": "",
                "visit_count": 0,
                "convert_count": 0
            }
    
    def format_file_size(self, size_in_bytes):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_in_bytes < 1024:
                return f"{size_in_bytes:.2f} {unit}"
            size_in_bytes /= 1024
        return f"{size_in_bytes:.2f} TB" 