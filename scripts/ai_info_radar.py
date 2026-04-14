#!/usr/bin/env python3
"""
AI信息雷达 - 主入口
处理用户请求，协调各模块
"""

import sys
import os
import json
import re
from typing import List, Dict, Optional

# 添加脚本目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from resource_db import ResourceDB, get_db
from card_formatter import CardFormatter
from content_fetcher import ContentFetcher
from bookmark_manager import BookmarkManager, get_manager as get_bookmark_manager
from schedule_manager import ScheduleManager, get_manager as get_schedule_manager

class AIInfoRadar:
    """AI信息雷达主类"""
    
    def __init__(self, user_id: str = "default"):
        """初始化"""
        self.user_id = user_id
        self.db = get_db()
        self.fetcher = ContentFetcher()
        self.formatter = CardFormatter()
        self.bookmark_mgr = get_bookmark_manager(user_id)
        self.schedule_mgr = get_schedule_manager(user_id)
    
    def process(self, query: str) -> str:
        """处理用户请求"""
        query = query.strip()
        
        # 1. 资源查询
        if self._match_category_query(query):
            return self._handle_category_query(query)
        
        # 2. 最新内容查询
        if self._match_latest_query(query):
            return self._handle_latest_query(query)
        
        # 3. 搜索
        if self._match_search_query(query):
            return self._handle_search_query(query)
        
        # 4. 推荐
        if self._match_recommend_query(query):
            return self._handle_recommend_query(query)
        
        # 5. 收藏管理
        if self._match_bookmark_query(query):
            return self._handle_bookmark_query(query)
        
        # 6. 定时推送
        if self._match_schedule_query(query):
            return self._handle_schedule_query(query)
        
        # 7. 帮助
        if self._match_help_query(query):
            return self.formatter.format_help()
        
        # 默认：智能匹配
        return self._handle_smart_match(query)
    
    def _match_category_query(self, query: str) -> bool:
        """匹配分类查询"""
        patterns = [
            r'(AI|人工智能).*(媒体|公众号|博客|播客|书籍|视频|课程)',
            r'推荐.*(AI|人工智能)',
            r'(媒体|公众号|博客|播客|书籍|视频|课程).*推荐',
            r'有.*(媒体|公众号|博客|播客|书籍|视频|课程)',
            r'(国内|中文|英文).*(媒体|资源)',
        ]
        for p in patterns:
            if re.search(p, query, re.I):
                return True
        return False
    
    def _handle_category_query(self, query: str) -> str:
        """处理分类查询"""
        # 判断分类
        if '媒体' in query or '公众号' in query:
            resources = self.db.get_resources_by_category("domestic_media")
            resources.extend(self.db.get_resources_by_category("twitter"))
            return self.formatter.format_resource_list(resources, "AI媒体推荐")
        
        elif '播客' in query:
            resources = self.db.get_resources_by_category("podcasts")
            return self.formatter.format_resource_list(resources, "AI播客推荐")
        
        elif '书籍' in query or '书' in query:
            resources = self.db.get_resources_by_category("books")
            return self.formatter.format_resource_list(resources, "AI书籍推荐")
        
        elif '视频' in query or '课程' in query:
            resources = self.db.get_resources_by_category("videos")
            return self.formatter.format_resource_list(resources, "AI视频/课程推荐")
        
        elif '博客' in query:
            resources = self.db.get_resources_by_category("blogs")
            return self.formatter.format_resource_list(resources, "AI博客推荐")
        
        else:
            # 默认返回所有分类
            return self._show_all_categories()
    
    def _match_latest_query(self, query: str) -> bool:
        """匹配最新内容查询"""
        patterns = [
            r'(最近|这两天|最新|最近).*(发了什么|文章|内容|动态)',
            r'(搜|搜索|查找).*(最新|recent)',
        ]
        for p in patterns:
            if re.search(p, query, re.I):
                return True
        return False
    
    def _handle_latest_query(self, query: str) -> str:
        """处理最新内容查询"""
        # 提取媒体名称
        media_names = [r.get("name") for r in self.db.get_all_resources()]
        
        for media_name in media_names:
            if media_name in query:
                resource = self.db.get_resource_by_name(media_name)
                if resource:
                    contents = self.fetcher.fetch_media_latest(
                        resource.get("id", ""),
                        resource,
                        days=2
                    )
                    
                    if not contents:
                        return f"📭 **{media_name}**\n\n暂时无法获取最新内容，建议直接访问：\n{resource.get('website', '') or '公众号: ' + resource.get('wechat', '')}"
                    
                    lines = [f"## 📰 {media_name} 最新内容", ""]
                    for content in contents[:5]:
                        lines.append(self.formatter.format_content_card(content))
                        lines.append("---")
                    
                    return "\n".join(lines)
        
        # 搜索主题
        topic_match = re.search(r'搜\s*(.+?)\s*最新', query)
        if topic_match:
            topic = topic_match.group(1)
            contents = self.fetcher.fetch_topic_content(topic, self.db, limit=10)
            
            if not contents:
                return f"📭 未找到「{topic}」的最新内容"
            
            lines = [f"## 🔍 「{topic}」最新动态", ""]
            for content in contents[:5]:
                lines.append(self.formatter.format_content_card(content))
                lines.append("---")
            
            return "\n".join(lines)
        
        return "请指定媒体名称或搜索关键词，例如：\n- 机器之心这两天发了什么\n- 搜 OpenClaw 最新"
    
    def _match_search_query(self, query: str) -> bool:
        """匹配搜索查询"""
        return '搜' in query and '最新' not in query
    
    def _handle_search_query(self, query: str) -> str:
        """处理搜索查询"""
        # 提取搜索词
        search_term = query.replace('搜', '').strip()
        
        results = self.db.search_resources(search_term, limit=15)
        return self.formatter.format_search_results(search_term, results)
    
    def _match_recommend_query(self, query: str) -> bool:
        """匹配推荐查询"""
        patterns = [
            r'(适合|推荐).*(小白|入门|初学者|新手)',
            r'(技术向|专业|进阶).*(推荐|资源)',
            r'(中文|英文).*(资源|推荐)',
        ]
        for p in patterns:
            if re.search(p, query, re.I):
                return True
        return False
    
    def _handle_recommend_query(self, query: str) -> str:
        """处理推荐查询"""
        if '小白' in query or '入门' in query or '初学' in query:
            resources = self.db.recommend_for_beginner()
            return self.formatter.format_recommendation(resources, "小白入门")
        
        elif '技术' in query or '专业' in query:
            resources = self.db.recommend_for_professional()
            return self.formatter.format_recommendation(resources, "技术进阶")
        
        elif '中文' in query:
            resources = self.db.get_resources_by_language("中文")
            return self.formatter.format_recommendation(resources[:10], "中文资源")
        
        elif '英文' in query:
            resources = self.db.get_resources_by_language("英文")
            return self.formatter.format_recommendation(resources[:10], "英文资源")
        
        else:
            # 默认推荐
            resources = self.db.recommend_for_beginner()[:5]
            resources.extend(self.db.recommend_for_professional()[:5])
            return self.formatter.format_recommendation(resources, "AI学习")
    
    def _match_bookmark_query(self, query: str) -> bool:
        """匹配收藏查询"""
        patterns = [
            r'收藏(这个|该资源)?',
            r'我的收藏',
            r'我的书单',
            r'取消收藏',
        ]
        for p in patterns:
            if re.search(p, query, re.I):
                return True
        return False
    
    def _handle_bookmark_query(self, query: str) -> str:
        """处理收藏查询"""
        if '收藏这个' in query or '加入收藏' in query:
            # 这里需要上下文获取当前资源
            return "💡 请在查看资源详情后使用 `收藏这个` 收藏"
        
        elif '我的收藏' in query or '我的书单' in query:
            bookmarks = self.bookmark_mgr.get_all_bookmarks()
            return self.formatter.format_bookmark_list(bookmarks)
        
        elif '取消收藏' in query:
            return "请使用 `取消收藏 资源名称` 移除收藏"
        
        return self.formatter.format_bookmark_list(self.bookmark_mgr.get_all_bookmarks())
    
    def _match_schedule_query(self, query: str) -> bool:
        """匹配定时推送查询"""
        patterns = [
            r'(设置|创建).*(推送|定时|订阅)',
            r'(查看|管理).*(推送|定时)',
            r'(取消|删除|关闭).*(推送|定时)',
        ]
        for p in patterns:
            if re.search(p, query, re.I):
                return True
        return False
    
    def _handle_schedule_query(self, query: str) -> str:
        """处理定时推送查询"""
        if '设置' in query or '创建' in query:
            # 解析设置
            # 格式: 设置 频率 推送 主题
            freq_match = re.search(r'(每小时|每3小时|每6小时|每日.*?点|每周.)', query)
            topic_match = re.search(r'推送\s*(.+?)(?:资讯|内容|文章)?(?:\s|$)', query)
            
            if freq_match:
                frequency = freq_match.group(1)
                topic = topic_match.group(1) if topic_match else "全部"
                
                result = self.schedule_mgr.add_schedule(frequency, topic)
                
                if result["success"]:
                    s = result["schedule"]
                    return f"✅ 推送设置成功！\n\n📅 频率: {s['frequency_name']}\n🏷️ 主题: {s['topic']}\n📊 数量: {s['count']}条\n🎯 对象: {s['target']}"
                else:
                    return f"❌ 设置失败: {result.get('error')}"
            else:
                # 显示频率选项
                options = self.schedule_mgr.get_frequency_options()
                return f"请选择推送频率:\n" + "\n".join([f"  - {o}" for o in options[:5]])
        
        elif '查看' in query or '管理' in query:
            schedules = self.schedule_mgr.get_all_schedules()
            return self.formatter.format_schedule_settings(schedules)
        
        elif '取消' in query or '删除' in query or '关闭' in query:
            return "请使用 `取消推送 设置ID` 关闭特定推送"
        
        return self.formatter.format_schedule_settings(self.schedule_mgr.get_all_schedules())
    
    def _match_help_query(self, query: str) -> bool:
        """匹配帮助查询"""
        return query in ['帮助', 'help', '怎么用', '使用说明']
    
    def _show_all_categories(self) -> str:
        """显示所有分类"""
        lines = ["## 📚 AI学习资源分类", ""]
        
        categories = self.db.get_all_categories()
        for cat_id, cat_name in categories.items():
            count = len(self.db.get_resources_by_category(cat_id))
            lines.append(f"- **{cat_name}**: {count} 个资源")
        
        lines.append("")
        lines.append("使用方式:")
        lines.append("- `AI媒体推荐` - 查看媒体列表")
        lines.append("- `AI播客有哪些` - 查看播客推荐")
        lines.append("- `AI书籍推荐` - 查看书单")
        
        return "\n".join(lines)
    
    def _handle_smart_match(self, query: str) -> str:
        """智能匹配"""
        # 尝试搜索
        results = self.db.search_resources(query, limit=5)
        
        if results:
            return self.formatter.format_search_results(query, results)
        
        # 默认帮助
        return f"未能理解「{query}」\n\n" + self.formatter.format_help()


def main():
    """主函数"""
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = sys.stdin.read().strip()
    
    if not query:
        print(CardFormatter.format_help())
        return
    
    radar = AIInfoRadar()
    result = radar.process(query)
    print(result)


if __name__ == "__main__":
    main()
