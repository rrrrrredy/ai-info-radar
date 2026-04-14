#!/usr/bin/env python3
"""
AI信息雷达 - 定时推送管理器
管理定时推送任务
"""

import json
import os
from typing import List, Dict, Optional
from datetime import datetime

class ScheduleManager:
    """定时推送管理器"""
    
    # 频率映射
    FREQUENCY_MAP = {
        "每小时": "0 * * * *",
        "每3小时": "0 */3 * * *",
        "每6小时": "0 */6 * * *",
        "每日早9点": "0 9 * * *",
        "每日早8点": "0 8 * * *",
        "每日晚6点": "0 18 * * *",
        "每日晚9点": "0 21 * * *",
        "每周一": "0 9 * * 1",
        "每周五": "0 18 * * 5",
        "每周日": "0 20 * * 0"
    }
    
    # 主题映射
    TOPIC_MAP = {
        "全部": "all",
        "Agent": "agent",
        "AI Agent": "agent",
        "大模型": "llm",
        "多模态": "multimodal",
        "AI安全": "safety",
        "AI产品": "product",
        "AI创业": "startup"
    }
    
    def __init__(self, user_id: str = "default"):
        """初始化管理器"""
        self.user_id = user_id
        self.config_dir = os.path.expanduser("~/.ai-info-radar")
        self.schedule_file = os.path.join(self.config_dir, f"schedule_{user_id}.json")
        
        os.makedirs(self.config_dir, exist_ok=True)
        self.schedules = self._load_schedules()
    
    def _load_schedules(self) -> List[Dict]:
        """加载推送设置"""
        try:
            if os.path.exists(self.schedule_file):
                with open(self.schedule_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading schedules: {e}")
        
        return []
    
    def _save_schedules(self):
        """保存推送设置"""
        try:
            with open(self.schedule_file, 'w', encoding='utf-8') as f:
                json.dump(self.schedules, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving schedules: {e}")
    
    def add_schedule(self, frequency: str, topic: str = "全部", 
                     count: int = 3, target: str = "个人", media: str = None) -> Dict:
        """添加定时推送"""
        # 验证频率
        if frequency not in self.FREQUENCY_MAP:
            # 尝试匹配
            matched = False
            for freq_name in self.FREQUENCY_MAP:
                if frequency in freq_name or freq_name in frequency:
                    frequency = freq_name
                    matched = True
                    break
            
            if not matched:
                return {"success": False, "error": f"不支持的频率: {frequency}"}
        
        # 验证主题
        topic_key = self.TOPIC_MAP.get(topic, topic.lower())
        
        # 创建推送配置
        schedule = {
            "id": f"schedule_{len(self.schedules) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "frequency_name": frequency,
            "frequency_cron": self.FREQUENCY_MAP[frequency],
            "topic": topic,
            "topic_key": topic_key,
            "count": min(max(count, 1), 10),  # 限制1-10条
            "target": target,
            "media": media,  # 特定媒体
            "enabled": True,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "last_run": None,
            "run_count": 0
        }
        
        self.schedules.append(schedule)
        self._save_schedules()
        
        return {"success": True, "schedule": schedule}
    
    def remove_schedule(self, schedule_id: str) -> bool:
        """移除推送设置"""
        for i, s in enumerate(self.schedules):
            if s.get("id") == schedule_id:
                self.schedules.pop(i)
                self._save_schedules()
                return True
        
        return False
    
    def update_schedule(self, schedule_id: str, **kwargs) -> bool:
        """更新推送设置"""
        for s in self.schedules:
            if s.get("id") == schedule_id:
                # 更新字段
                for key, value in kwargs.items():
                    if key in ["frequency", "frequency_name"]:
                        if value in self.FREQUENCY_MAP:
                            s["frequency_name"] = value
                            s["frequency_cron"] = self.FREQUENCY_MAP[value]
                    elif key == "topic":
                        s["topic"] = value
                        s["topic_key"] = self.TOPIC_MAP.get(value, value.lower())
                    elif key == "count":
                        s["count"] = min(max(value, 1), 10)
                    elif key == "enabled":
                        s["enabled"] = bool(value)
                    elif key == "target":
                        s["target"] = value
                    elif key == "media":
                        s["media"] = value
                
                self._save_schedules()
                return True
        
        return False
    
    def get_all_schedules(self) -> List[Dict]:
        """获取所有推送设置"""
        return self.schedules
    
    def get_enabled_schedules(self) -> List[Dict]:
        """获取启用的推送设置"""
        return [s for s in self.schedules if s.get("enabled", True)]
    
    def get_schedule_by_id(self, schedule_id: str) -> Optional[Dict]:
        """通过ID获取推送设置"""
        for s in self.schedules:
            if s.get("id") == schedule_id:
                return s
        return None
    
    def toggle_schedule(self, schedule_id: str) -> bool:
        """切换推送开关"""
        for s in self.schedules:
            if s.get("id") == schedule_id:
                s["enabled"] = not s.get("enabled", True)
                self._save_schedules()
                return True
        
        return False
    
    def get_frequency_options(self) -> List[str]:
        """获取频率选项"""
        return list(self.FREQUENCY_MAP.keys())
    
    def get_topic_options(self) -> List[str]:
        """获取主题选项"""
        return list(self.TOPIC_MAP.keys())
    
    def should_run_now(self, schedule: Dict) -> bool:
        """检查是否应该现在执行"""
        if not schedule.get("enabled", True):
            return False
        
        # 这里可以实现更复杂的逻辑
        # 简化版本：检查是否到了执行时间
        return True
    
    def record_run(self, schedule_id: str):
        """记录执行"""
        for s in self.schedules:
            if s.get("id") == schedule_id:
                s["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                s["run_count"] = s.get("run_count", 0) + 1
                self._save_schedules()
                break
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "total": len(self.schedules),
            "enabled": len([s for s in self.schedules if s.get("enabled", True)]),
            "disabled": len([s for s in self.schedules if not s.get("enabled", True)]),
            "by_frequency": self._group_by("frequency_name"),
            "by_topic": self._group_by("topic")
        }
    
    def _group_by(self, key: str) -> Dict:
        """按字段分组统计"""
        groups = {}
        for s in self.schedules:
            value = s.get(key, "未知")
            groups[value] = groups.get(value, 0) + 1
        return groups
    
    def export_config(self) -> str:
        """导出配置"""
        return json.dumps(self.schedules, ensure_ascii=False, indent=2)
    
    def import_config(self, config_str: str) -> bool:
        """导入配置"""
        try:
            schedules = json.loads(config_str)
            if isinstance(schedules, list):
                self.schedules = schedules
                self._save_schedules()
                return True
        except Exception as e:
            print(f"Import error: {e}")
        
        return False


# 便捷函数
def get_manager(user_id: str = "default") -> ScheduleManager:
    """获取管理器实例"""
    return ScheduleManager(user_id)


if __name__ == "__main__":
    # 测试
    manager = ScheduleManager("test")
    
    print("=== 频率选项 ===")
    for f in manager.get_frequency_options():
        print(f"  {f}")
    
    print("\n=== 主题选项 ===")
    for t in manager.get_topic_options():
        print(f"  {t}")
    
    print("\n=== 添加推送 ===")
    result = manager.add_schedule("每小时", "Agent", 3)
    print(result)
    
    print("\n=== 推送列表 ===")
    print(manager.get_all_schedules())
