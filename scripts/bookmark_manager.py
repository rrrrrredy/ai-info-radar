#!/usr/bin/env python3
"""
AI信息雷达 - 收藏管理器
管理用户收藏的资源
"""

import json
import os
from typing import List, Dict, Optional
from datetime import datetime

class BookmarkManager:
    """收藏管理器"""
    
    def __init__(self, user_id: str = "default"):
        """初始化收藏管理器"""
        self.user_id = user_id
        self.config_dir = os.path.expanduser("~/.ai-info-radar")
        self.bookmarks_file = os.path.join(self.config_dir, f"bookmarks_{user_id}.json")
        
        # 确保目录存在
        os.makedirs(self.config_dir, exist_ok=True)
        
        # 加载收藏
        self.bookmarks = self._load_bookmarks()
    
    def _load_bookmarks(self) -> List[Dict]:
        """加载收藏"""
        try:
            if os.path.exists(self.bookmarks_file):
                with open(self.bookmarks_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading bookmarks: {e}")
        
        return []
    
    def _save_bookmarks(self):
        """保存收藏"""
        try:
            with open(self.bookmarks_file, 'w', encoding='utf-8') as f:
                json.dump(self.bookmarks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving bookmarks: {e}")
    
    def add_bookmark(self, resource: Dict, note: str = "") -> bool:
        """添加收藏"""
        # 检查是否已存在
        resource_id = resource.get("id") or resource.get("name")
        
        for bm in self.bookmarks:
            existing_id = bm.get("resource", {}).get("id") or bm.get("resource", {}).get("name")
            if existing_id == resource_id:
                return False  # 已存在
        
        # 添加新收藏
        bookmark = {
            "resource": resource,
            "note": note,
            "added_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "tags": []
        }
        
        self.bookmarks.append(bookmark)
        self._save_bookmarks()
        return True
    
    def remove_bookmark(self, resource_id: str) -> bool:
        """移除收藏"""
        for i, bm in enumerate(self.bookmarks):
            existing_id = bm.get("resource", {}).get("id") or bm.get("resource", {}).get("name")
            if existing_id == resource_id:
                self.bookmarks.pop(i)
                self._save_bookmarks()
                return True
        
        return False
    
    def get_all_bookmarks(self) -> List[Dict]:
        """获取所有收藏"""
        return self.bookmarks
    
    def get_bookmarks_by_category(self, category: str) -> List[Dict]:
        """按分类获取收藏"""
        return [
            bm for bm in self.bookmarks
            if bm.get("resource", {}).get("category") == category
        ]
    
    def get_bookmarks_by_tag(self, tag: str) -> List[Dict]:
        """按标签获取收藏"""
        return [
            bm for bm in self.bookmarks
            if tag in bm.get("tags", [])
        ]
    
    def search_bookmarks(self, query: str) -> List[Dict]:
        """搜索收藏"""
        results = []
        query_lower = query.lower()
        
        for bm in self.bookmarks:
            resource = bm.get("resource", {})
            
            # 搜索名称
            if query_lower in resource.get("name", "").lower():
                results.append(bm)
                continue
            
            # 搜索描述
            if query_lower in resource.get("description", "").lower():
                results.append(bm)
                continue
            
            # 搜索关注领域
            for focus in resource.get("focus", []):
                if query_lower in focus.lower():
                    results.append(bm)
                    break
        
        return results
    
    def add_tag(self, resource_id: str, tag: str) -> bool:
        """添加标签"""
        for bm in self.bookmarks:
            existing_id = bm.get("resource", {}).get("id") or bm.get("resource", {}).get("name")
            if existing_id == resource_id:
                if tag not in bm.get("tags", []):
                    bm.setdefault("tags", []).append(tag)
                    self._save_bookmarks()
                return True
        
        return False
    
    def remove_tag(self, resource_id: str, tag: str) -> bool:
        """移除标签"""
        for bm in self.bookmarks:
            existing_id = bm.get("resource", {}).get("id") or bm.get("resource", {}).get("name")
            if existing_id == resource_id:
                if tag in bm.get("tags", []):
                    bm["tags"].remove(tag)
                    self._save_bookmarks()
                return True
        
        return False
    
    def update_note(self, resource_id: str, note: str) -> bool:
        """更新备注"""
        for bm in self.bookmarks:
            existing_id = bm.get("resource", {}).get("id") or bm.get("resource", {}).get("name")
            if existing_id == resource_id:
                bm["note"] = note
                self._save_bookmarks()
                return True
        
        return False
    
    def is_bookmarked(self, resource_id: str) -> bool:
        """检查是否已收藏"""
        for bm in self.bookmarks:
            existing_id = bm.get("resource", {}).get("id") or bm.get("resource", {}).get("name")
            if existing_id == resource_id:
                return True
        
        return False
    
    def get_stats(self) -> Dict:
        """获取收藏统计"""
        stats = {
            "total": len(self.bookmarks),
            "by_category": {},
            "by_difficulty": {},
            "by_language": {}
        }
        
        for bm in self.bookmarks:
            resource = bm.get("resource", {})
            
            # 分类统计
            category = resource.get("category_name", "其他")
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            
            # 难度统计
            difficulty = resource.get("difficulty", "未知")
            stats["by_difficulty"][difficulty] = stats["by_difficulty"].get(difficulty, 0) + 1
            
            # 语言统计
            language = resource.get("language", "未知")
            stats["by_language"][language] = stats["by_language"].get(language, 0) + 1
        
        return stats


# 便捷函数
def get_manager(user_id: str = "default") -> BookmarkManager:
    """获取收藏管理器实例"""
    return BookmarkManager(user_id)


if __name__ == "__main__":
    # 测试
    manager = BookmarkManager("test")
    
    # 添加测试收藏
    test_resource = {
        "id": "jiqizhixin",
        "name": "机器之心",
        "category": "domestic_media",
        "category_name": "国内自媒体",
        "description": "AI技术媒体"
    }
    
    print("添加收藏:", manager.add_bookmark(test_resource, "测试备注"))
    print("收藏列表:", len(manager.get_all_bookmarks()))
    print("统计:", manager.get_stats())
