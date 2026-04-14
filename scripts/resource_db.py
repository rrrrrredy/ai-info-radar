#!/usr/bin/env python3
"""
AI信息雷达 - 资源数据库管理
管理所有AI学习资源，提供查询、搜索、分类功能
"""

import json
import os
from typing import List, Dict, Optional, Any
from fuzzywuzzy import fuzz

class ResourceDB:
    """资源数据库管理类"""
    
    def __init__(self, data_path: Optional[str] = None):
        """初始化数据库"""
        if data_path is None:
            # 获取skill目录路径
            skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_path = os.path.join(skill_dir, 'data', 'resources.json')
        
        self.data_path = data_path
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """加载资源数据"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading resources: {e}")
            return {"categories": {}, "keywords": {}}
    
    def get_all_categories(self) -> Dict[str, str]:
        """获取所有分类"""
        return {
            cat_id: cat_data.get("name", cat_id)
            for cat_id, cat_data in self.data.get("categories", {}).items()
        }
    
    def get_resources_by_category(self, category: str) -> List[Dict]:
        """按分类获取资源"""
        cat_data = self.data.get("categories", {}).get(category, {})
        return cat_data.get("resources", [])
    
    def get_all_resources(self) -> List[Dict]:
        """获取所有资源"""
        all_resources = []
        for cat_id, cat_data in self.data.get("categories", {}).items():
            for resource in cat_data.get("resources", []):
                resource_copy = resource.copy()
                resource_copy["category"] = cat_id
                resource_copy["category_name"] = cat_data.get("name", cat_id)
                all_resources.append(resource_copy)
        return all_resources
    
    def search_resources(self, query: str, limit: int = 10) -> List[Dict]:
        """模糊搜索资源"""
        all_resources = self.get_all_resources()
        results = []
        
        for resource in all_resources:
            # 计算匹配分数
            name_score = fuzz.partial_ratio(query.lower(), resource.get("name", "").lower())
            desc_score = fuzz.partial_ratio(query.lower(), resource.get("description", "").lower())
            focus_score = 0
            for focus in resource.get("focus", []):
                focus_score = max(focus_score, fuzz.partial_ratio(query.lower(), focus.lower()))
            
            max_score = max(name_score, desc_score, focus_score)
            
            if max_score > 50:  # 阈值
                resource_copy = resource.copy()
                resource_copy["match_score"] = max_score
                results.append(resource_copy)
        
        # 按匹配分数排序
        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results[:limit]
    
    def get_resource_by_id(self, resource_id: str) -> Optional[Dict]:
        """通过ID获取资源"""
        for resource in self.get_all_resources():
            if resource.get("id") == resource_id:
                return resource
        return None
    
    def get_resource_by_name(self, name: str) -> Optional[Dict]:
        """通过名称获取资源（模糊匹配）"""
        for resource in self.get_all_resources():
            if resource.get("name") == name:
                return resource
            # 模糊匹配
            if fuzz.ratio(name.lower(), resource.get("name", "").lower()) > 80:
                return resource
        return None
    
    def get_resources_by_difficulty(self, difficulty: str) -> List[Dict]:
        """按难度获取资源"""
        return [
            r for r in self.get_all_resources()
            if r.get("difficulty") == difficulty
        ]
    
    def get_resources_by_language(self, language: str) -> List[Dict]:
        """按语言获取资源"""
        return [
            r for r in self.get_all_resources()
            if language in r.get("language", "")
        ]
    
    def get_resources_by_focus(self, focus_keyword: str) -> List[Dict]:
        """按关注领域获取资源"""
        results = []
        for resource in self.get_all_resources():
            for focus in resource.get("focus", []):
                if fuzz.partial_ratio(focus_keyword.lower(), focus.lower()) > 70:
                    results.append(resource)
                    break
        return results
    
    def get_keywords(self, topic: str) -> List[str]:
        """获取主题关键词"""
        return self.data.get("keywords", {}).get(topic.lower(), [])
    
    def recommend_for_beginner(self) -> List[Dict]:
        """推荐适合小白的资源"""
        results = []
        for resource in self.get_all_resources():
            if resource.get("difficulty") in ["入门", "通俗"]:
                results.append(resource)
        return results[:10]
    
    def recommend_for_professional(self) -> List[Dict]:
        """推荐专业级资源"""
        results = []
        for resource in self.get_all_resources():
            if resource.get("difficulty") == "专业":
                results.append(resource)
        return results[:10]
    
    def get_media_with_wechat(self) -> List[Dict]:
        """获取有公众号的媒体"""
        return [
            r for r in self.get_all_resources()
            if r.get("wechat") or r.get("type", "").startswith("wechat")
        ]
    
    def get_media_with_website(self) -> List[Dict]:
        """获取有网站的媒体"""
        return [
            r for r in self.get_all_resources()
            if r.get("website") or r.get("type", "").startswith("website")
        ]
    
    def get_media_with_rss(self) -> List[Dict]:
        """获取有RSS的媒体"""
        return [
            r for r in self.get_all_resources()
            if r.get("rss")
        ]


# 便捷函数
def get_db() -> ResourceDB:
    """获取数据库实例"""
    return ResourceDB()


if __name__ == "__main__":
    # 测试
    db = ResourceDB()
    print("=== 所有分类 ===")
    for cat_id, cat_name in db.get_all_categories().items():
        print(f"  {cat_id}: {cat_name}")
    
    print("\n=== 搜索 '机器' ===")
    results = db.search_resources("机器")
    for r in results[:3]:
        print(f"  {r['name']} (score: {r['match_score']})")
    
    print("\n=== 小白推荐 ===")
    for r in db.recommend_for_beginner()[:3]:
        print(f"  {r['name']} - {r.get('difficulty')}")
