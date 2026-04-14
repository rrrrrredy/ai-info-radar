#!/usr/bin/env python3
"""
AI信息雷达 - 卡片格式生成器
生成美观的卡片式输出
"""

from typing import List, Dict, Optional
from datetime import datetime

class CardFormatter:
    """卡片格式生成器"""
    
    # 表情符号映射
    CATEGORY_EMOJI = {
        "domestic_media": "🇨🇳",
        "twitter": "🐦",
        "blogs": "📝",
        "podcasts": "🎙️",
        "books": "📚",
        "videos": "🎬"
    }
    
    DIFFICULTY_EMOJI = {
        "入门": "🌱",
        "通俗": "📖",
        "中等": "📊",
        "专业": "🔬"
    }
    
    TYPE_EMOJI = {
        "website": "🌐",
        "wechat": "💬",
        "website+wechat": "🌐💬",
        "twitter": "🐦",
        "podcast": "🎙️",
        "video": "🎬",
        "book": "📚"
    }
    
    @classmethod
    def format_resource_card(cls, resource: Dict, show_category: bool = True) -> str:
        """格式化单个资源卡片"""
        lines = []
        
        # 标题行
        category = resource.get("category", "")
        cat_emoji = cls.CATEGORY_EMOJI.get(category, "📌")
        name = resource.get("name", "未知")
        
        lines.append(f"{cat_emoji} **{name}**")
        lines.append("")
        
        # 元信息行
        meta_parts = []
        
        # 难度
        difficulty = resource.get("difficulty", "")
        if difficulty:
            diff_emoji = cls.DIFFICULTY_EMOJI.get(difficulty, "")
            meta_parts.append(f"{diff_emoji} {difficulty}")
        
        # 语言
        language = resource.get("language", "")
        if language:
            lang_emoji = "🇨🇳" if "中文" in language else "🇺🇸"
            meta_parts.append(f"{lang_emoji} {language}")
        
        # 类型
        resource_type = resource.get("type", "")
        if resource_type:
            type_emoji = cls.TYPE_EMOJI.get(resource_type, "📄")
            meta_parts.append(f"{type_emoji} {resource_type}")
        
        if meta_parts:
            lines.append(" | ".join(meta_parts))
            lines.append("")
        
        # 描述
        description = resource.get("description", "")
        if description:
            lines.append(f"> {description}")
            lines.append("")
        
        # 关注领域
        focus = resource.get("focus", [])
        if focus:
            focus_tags = " ".join([f"`{f}`" for f in focus[:5]])
            lines.append(f"🏷️ {focus_tags}")
            lines.append("")
        
        # 链接
        links = []
        if resource.get("website"):
            links.append(f"[🌐 网站]({resource['website']})")
        if resource.get("wechat"):
            links.append(f"[💬 公众号: {resource['wechat']}]")
        if resource.get("twitter"):
            links.append(f"[🐦 Twitter: @{resource['twitter']}](https://twitter.com/{resource['twitter']})")
        
        if links:
            lines.append(" | ".join(links))
        
        return "\n".join(lines)
    
    @classmethod
    def format_content_card(cls, content: Dict) -> str:
        """格式化内容卡片（最新文章/动态）"""
        lines = []
        
        # 媒体名称和时间
        source = content.get("source", "未知来源")
        published = content.get("published", "")
        
        lines.append(f"📰 **{source}**")
        if published:
            lines.append(f"⏱️ {published}")
        lines.append("")
        
        # 标题
        title = content.get("title", "")
        if title:
            lines.append(f"### {title}")
            lines.append("")
        
        # 摘要
        summary = content.get("summary", "")
        if summary:
            # 截断长摘要
            if len(summary) > 150:
                summary = summary[:150] + "..."
            lines.append(f"> {summary}")
            lines.append("")
        
        # 标签
        tags = content.get("tags", [])
        if tags:
            tag_str = " ".join([f"`{t}`" for t in tags[:5]])
            lines.append(f"🏷️ {tag_str}")
            lines.append("")
        
        # 操作按钮
        actions = []
        if content.get("url"):
            actions.append(f"[🔗 阅读原文]({content['url']})")
        actions.append("💾 收藏")
        actions.append("📤 分享")
        
        lines.append(" | ".join(actions))
        
        return "\n".join(lines)
    
    @classmethod
    def format_resource_list(cls, resources: List[Dict], title: str = "资源列表") -> str:
        """格式化资源列表"""
        lines = []
        lines.append(f"## {title}")
        lines.append("")
        lines.append(f"共找到 **{len(resources)}** 个资源")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        for i, resource in enumerate(resources[:20], 1):  # 最多显示20个
            lines.append(f"### {i}. {resource.get('name', '未知')}")
            lines.append("")
            
            # 简要信息
            meta = []
            if resource.get("difficulty"):
                meta.append(resource["difficulty"])
            if resource.get("language"):
                meta.append(resource["language"])
            if resource.get("category_name"):
                meta.append(resource["category_name"])
            
            if meta:
                lines.append(f"*{', '.join(meta)}*")
            
            if resource.get("description"):
                desc = resource["description"]
                if len(desc) > 100:
                    desc = desc[:100] + "..."
                lines.append(f"> {desc}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    @classmethod
    def format_recommendation(cls, resources: List[Dict], user_type: str = "") -> str:
        """格式化推荐结果"""
        lines = []
        
        if user_type:
            lines.append(f"## 🎯 为{user_type}推荐的AI资源")
        else:
            lines.append("## 🎯 AI资源推荐")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        
        for resource in resources[:10]:
            lines.append(cls.format_resource_card(resource))
            lines.append("")
            lines.append("---")
            lines.append("")
        
        return "\n".join(lines)
    
    @classmethod
    def format_search_results(cls, query: str, results: List[Dict]) -> str:
        """格式化搜索结果"""
        lines = []
        lines.append(f"## 🔍 「{query}」的搜索结果")
        lines.append("")
        
        if not results:
            lines.append("未找到相关资源，建议尝试其他关键词。")
            return "\n".join(lines)
        
        lines.append(f"找到 **{len(results)}** 个相关资源")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        for i, result in enumerate(results[:15], 1):
            match_score = result.get("match_score", 0)
            lines.append(f"### {i}. {result.get('name', '未知')} (匹配度: {match_score}%)")
            lines.append("")
            
            if result.get("description"):
                lines.append(f"> {result['description']}")
            
            # 显示匹配原因
            focus = result.get("focus", [])
            if focus:
                lines.append(f"🏷️ 相关领域: {', '.join(focus[:3])}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    @classmethod
    def format_bookmark_list(cls, bookmarks: List[Dict]) -> str:
        """格式化收藏列表"""
        lines = []
        lines.append("## 💾 我的收藏")
        lines.append("")
        
        if not bookmarks:
            lines.append("暂无收藏，使用 `收藏这个` 添加资源。")
            return "\n".join(lines)
        
        lines.append(f"共收藏 **{len(bookmarks)}** 个资源")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        for i, bm in enumerate(bookmarks, 1):
            resource = bm.get("resource", {})
            added_time = bm.get("added_time", "")
            
            lines.append(f"### {i}. {resource.get('name', '未知')}")
            if added_time:
                lines.append(f"📅 收藏于: {added_time}")
            lines.append("")
        
        return "\n".join(lines)
    
    @classmethod
    def format_schedule_settings(cls, settings: List[Dict]) -> str:
        """格式化推送设置"""
        lines = []
        lines.append("## ⏰ 我的推送设置")
        lines.append("")
        
        if not settings:
            lines.append("暂无推送设置，使用 `设置推送` 创建。")
            return "\n".join(lines)
        
        for i, setting in enumerate(settings, 1):
            lines.append(f"### 设置 {i}")
            lines.append(f"- 📅 频率: {setting.get('frequency', '未设置')}")
            lines.append(f"- 🏷️ 主题: {setting.get('topic', '全部')}")
            lines.append(f"- 📊 数量: {setting.get('count', 1)} 条")
            lines.append(f"- 🎯 对象: {setting.get('target', '个人')}")
            lines.append(f"- ✅ 状态: {'开启' if setting.get('enabled', True) else '暂停'}")
            lines.append("")
        
        return "\n".join(lines)
    
    @classmethod
    def format_help(cls) -> str:
        """格式化帮助信息"""
        lines = []
        lines.append("## 🤖 AI信息雷达 - 使用指南")
        lines.append("")
        lines.append("### 📚 资源查询")
        lines.append("- `AI媒体推荐` - 查看所有AI媒体")
        lines.append("- `AI播客有哪些` - 查看播客推荐")
        lines.append("- `AI书籍推荐` - 查看书单")
        lines.append("- `AI视频推荐` - 查看视频课程")
        lines.append("")
        lines.append("### 🔍 最新内容")
        lines.append("- `机器之心这两天发了什么` - 查看媒体最新内容")
        lines.append("- `搜 OpenClaw 最新` - 搜索主题最新动态")
        lines.append("")
        lines.append("### 🎯 智能推荐")
        lines.append("- `适合小白的AI资源` - 入门推荐")
        lines.append("- `技术向AI媒体` - 专业推荐")
        lines.append("- `英文AI资源` - 英文资源")
        lines.append("")
        lines.append("### 💾 收藏管理")
        lines.append("- `收藏这个` - 收藏当前资源")
        lines.append("- `我的收藏` - 查看收藏列表")
        lines.append("")
        lines.append("### ⏰ 定时推送")
        lines.append("- `设置每小时推送 Agent 资讯` - 创建定时任务")
        lines.append("- `查看我的推送设置` - 管理推送")
        lines.append("")
        return "\n".join(lines)


if __name__ == "__main__":
    # 测试
    test_resource = {
        "name": "机器之心",
        "type": "website+wechat",
        "description": "国内老牌AI技术媒体",
        "difficulty": "专业",
        "language": "中文",
        "focus": ["前沿技术", "产业动态"],
        "website": "https://jiqizhixin.com",
        "wechat": "almosthuman2014",
        "category": "domestic_media",
        "category_name": "国内自媒体"
    }
    
    print(CardFormatter.format_resource_card(test_resource))
