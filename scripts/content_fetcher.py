#!/usr/bin/env python3
"""
AI信息雷达 - 内容抓取器
抓取各大媒体最新内容
"""

import os
import subprocess
import json
import re
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import feedparser
import requests
from bs4 import BeautifulSoup

class ContentFetcher:
    """内容抓取器"""
    
    def __init__(self):
        self.cache = {}  # 简单缓存
        self.cache_time = 300  # 缓存5分钟
    
    def fetch_from_rss(self, rss_url: str, limit: int = 5) -> List[Dict]:
        """从RSS feed抓取内容"""
        try:
            feed = feedparser.parse(rss_url)
            results = []
            
            for entry in feed.entries[:limit]:
                result = {
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "summary": entry.get("summary", entry.get("description", ""))[:200],
                    "published": self._parse_date(entry.get("published", "")),
                    "source": feed.feed.get("title", "未知来源")
                }
                results.append(result)
            
            return results
        except Exception as e:
            print(f"RSS fetch error: {e}")
            return []
    
    def fetch_from_website(self, url: str, limit: int = 5) -> List[Dict]:
        """从网站抓取最新文章"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 这里需要根据具体网站调整选择器
            # 通用策略：找文章列表
            articles = []
            
            # 尝试常见的文章选择器
            selectors = [
                'article', '.article', '.post', '.entry',
                '.news-item', '.blog-post', '[class*="article"]',
                'h2 a', 'h3 a', '.title a'
            ]
            
            for selector in selectors:
                items = soup.select(selector)[:limit]
                if items:
                    for item in items:
                        title = item.get_text(strip=True)
                        link = item.get('href', '')
                        if link and not link.startswith('http'):
                            link = url.rstrip('/') + '/' + link.lstrip('/')
                        
                        if title and len(title) > 10:
                            articles.append({
                                "title": title,
                                "url": link,
                                "summary": "",
                                "published": "近期",
                                "source": url
                            })
                    break
            
            return articles[:limit]
        except Exception as e:
            print(f"Website fetch error: {e}")
            return []
    
    def fetch_from_wechat(self, wechat_id: str, limit: int = 5) -> List[Dict]:
        """从公众号抓取最新文章（通过搜狗微信搜索）"""
        try:
            # 使用搜狗微信搜索
            search_url = f"https://weixin.sogou.com/weixin?type=1&query={wechat_id}"
            
            # Use web fetch tool
            result = subprocess.run(
                ["curl", "-s", search_url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # 解析结果
            content = result.stdout
            # 这里需要解析搜狗搜索结果提取文章列表
            # 由于反爬机制，可能需要更复杂的处理
            
            # 简化版本：返回提示信息
            return [{
                "title": f"请在微信搜索公众号: {wechat_id}",
                "url": f"https://weixin.qq.com",
                "summary": "由于微信反爬机制，建议直接在微信内查看最新文章",
                "published": "",
                "source": wechat_id
            }]
        except Exception as e:
            print(f"WeChat fetch error: {e}")
            return []
    
    def fetch_from_twitter(self, username: str, limit: int = 5) -> List[Dict]:
        """Fetch latest tweets using X/Twitter guest token GraphQL API (no login required)."""
        BEARER = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
        UA = "TwitterAndroid/10.21.0-release.0 (310210000-r-0) ONEPLUS+A3010/9 (OnePlus;ONEPLUS+A3010;OnePlus;OnePlus3;0;;1;2016)"

        try:
            # Step 1: Get guest token
            headers = {"Authorization": f"Bearer {BEARER}", "User-Agent": UA}
            proxy_url = os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")
            proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None

            r = requests.post(
                "https://api.twitter.com/1.1/guest/activate.json",
                headers=headers, proxies=proxies, timeout=15
            )
            guest_token = r.json()["guest_token"]

            # Step 2: Get user info
            gql_headers = {
                "Authorization": f"Bearer {BEARER}",
                "x-guest-token": guest_token,
                "User-Agent": UA,
                "x-twitter-client-language": "en",
                "x-twitter-active-user": "yes",
            }
            variables = json.dumps({"screen_name": username, "withSafetyModeUserFields": True})
            features = json.dumps({
                "hidden_profile_likes_enabled": True, "hidden_profile_subscriptions_enabled": True,
                "responsive_web_graphql_exclude_directive_enabled": True,
                "verified_phone_label_enabled": False,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                "responsive_web_graphql_timeline_navigation_enabled": True,
            })
            r2 = requests.get(
                "https://x.com/i/api/graphql/NimuplG1OB7Fd2btCLdBOw/UserByScreenName",
                params={"variables": variables, "features": features},
                headers=gql_headers, proxies=proxies, timeout=15
            )
            user_data = r2.json().get("data", {}).get("user", {}).get("result", {})
            user_id = user_data.get("rest_id", "")

            if not user_id:
                print(f"  Twitter: Could not resolve user @{username}")
                return []

            # Step 3: Get timeline
            tl_vars = json.dumps({"userId": user_id, "count": min(limit, 20),
                                  "includePromotedContent": False, "withVoice": True, "withV2Timeline": True})
            tl_feats = json.dumps({
                "rweb_tipjar_consumption_enabled": True,
                "responsive_web_graphql_exclude_directive_enabled": True,
                "verified_phone_label_enabled": False,
                "responsive_web_graphql_timeline_navigation_enabled": True,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                "communities_web_enable_tweet_community_results_fetch": True,
                "c9s_tweet_anatomy_moderator_badge_enabled": True,
                "tweetypie_unmention_optimization_enabled": True,
                "responsive_web_edit_tweet_api_enabled": True,
                "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
                "view_counts_everywhere_api_enabled": True,
                "longform_notetweets_consumption_enabled": True,
                "responsive_web_twitter_article_tweet_consumption_enabled": True,
                "tweet_awards_web_tipping_enabled": False,
                "creator_subscriptions_tweet_preview_api_enabled": True,
                "freedom_of_speech_not_reach_fetch_enabled": True,
                "standardized_nudges_misinfo": True,
                "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
                "rweb_video_timestamps_enabled": True,
                "longform_notetweets_rich_text_read_enabled": True,
                "longform_notetweets_inline_media_enabled": True,
                "responsive_web_enhance_cards_enabled": False,
            })
            rt = requests.get(
                "https://x.com/i/api/graphql/QWF3SzpHmykQHsQMixG0cg/UserTweets",
                params={"variables": tl_vars, "features": tl_feats},
                headers=gql_headers, proxies=proxies, timeout=15
            )

            results = []
            entries = []
            try:
                timeline = rt.json()["data"]["user"]["result"]["timeline_v2"]["timeline"]
                for instruction in timeline.get("instructions", []):
                    entries.extend(instruction.get("entries", []))
            except (KeyError, TypeError):
                pass

            for entry in entries:
                try:
                    tweet_result = entry["content"]["itemContent"]["tweet_results"]["result"]
                    legacy = tweet_result.get("legacy", {})
                    text = legacy.get("full_text", "")
                    tweet_id = legacy.get("id_str", tweet_result.get("rest_id", ""))
                    created_at = legacy.get("created_at", "")
                    if text:
                        results.append({
                            "title": text[:100] + ("..." if len(text) > 100 else ""),
                            "url": f"https://twitter.com/{username}/status/{tweet_id}",
                            "summary": text,
                            "published": created_at,
                            "source": f"@{username}",
                            "tags": ["Twitter"]
                        })
                except (KeyError, TypeError):
                    continue

            return results[:limit]
        except Exception as e:
            print(f"Twitter fetch error: {e}")
            return []
    
    def search_latest_content(self, keyword: str, days: int = 2, limit: int = 10) -> List[Dict]:
        """Search for latest content using Jina Search API (free, no API key required)."""
        results = []

        # 1. Use Jina Search API (https://s.jina.ai)
        try:
            search_url = f"https://s.jina.ai/{requests.utils.quote(keyword + ' AI news')}"
            headers = {"Accept": "application/json", "X-Retain-Images": "none"}
            proxy_url = os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")
            proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None

            r = requests.get(search_url, headers=headers, proxies=proxies, timeout=30)
            data = r.json()

            for item in data.get("data", [])[:limit]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "summary": item.get("description", "")[:200],
                    "published": "Recent",
                    "source": item.get("url", "").split("/")[2] if item.get("url") else "Web search",
                    "tags": [keyword]
                })
        except Exception as e:
            print(f"Jina search error: {e}")

        # 2. Fallback: DuckDuckGo HTML search (no API key needed)
        if not results:
            try:
                ddg_url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(keyword + ' AI news')}"
                r = requests.get(ddg_url, headers={"User-Agent": "Mozilla/5.0"}, proxies=proxies, timeout=15)
                soup = BeautifulSoup(r.text, "html.parser")
                for result_div in soup.select(".result__body")[:limit]:
                    title_el = result_div.select_one(".result__title a")
                    snippet_el = result_div.select_one(".result__snippet")
                    if title_el:
                        results.append({
                            "title": title_el.get_text(strip=True),
                            "url": title_el.get("href", ""),
                            "summary": snippet_el.get_text(strip=True) if snippet_el else "",
                            "published": "Recent",
                            "source": "DuckDuckGo",
                            "tags": [keyword]
                        })
            except Exception as e:
                print(f"DuckDuckGo fallback error: {e}")

        return results[:limit]
    
    def fetch_media_latest(self, media_id: str, media_config: Dict, days: int = 2) -> List[Dict]:
        """获取指定媒体的最新内容"""
        results = []
        
        # 根据媒体类型选择抓取方式
        if media_config.get("rss"):
            results = self.fetch_from_rss(media_config["rss"], limit=5)
        elif media_config.get("website"):
            results = self.fetch_from_website(media_config["website"], limit=5)
        elif media_config.get("twitter"):
            results = self.fetch_from_twitter(media_config["twitter"], limit=5)
        elif media_config.get("wechat"):
            results = self.fetch_from_wechat(media_config["wechat"], limit=5)
        
        # 过滤时间范围
        if days > 0:
            results = self._filter_by_date(results, days)
        
        # 添加来源信息
        for item in results:
            item["media_id"] = media_id
            item["media_name"] = media_config.get("name", "")
        
        return results
    
    def fetch_topic_content(self, topic: str, db, limit: int = 10) -> List[Dict]:
        """获取主题相关内容"""
        # 1. 获取主题关键词
        keywords = db.get_keywords(topic)
        
        # 2. 获取相关媒体
        resources = db.get_resources_by_focus(topic)
        
        # 3. 从相关媒体抓取内容
        all_content = []
        for resource in resources[:5]:  # 限制媒体数量
            if resource.get("rss") or resource.get("website") or resource.get("twitter"):
                content = self.fetch_media_latest(
                    resource.get("id", ""),
                    resource,
                    days=2
                )
                all_content.extend(content)
        
        # 4. 搜索关键词
        search_results = self.search_latest_content(topic, days=2, limit=limit)
        all_content.extend(search_results)
        
        # 5. 去重
        all_content = self._deduplicate(all_content)
        
        return all_content[:limit]
    
    def _parse_date(self, date_str: str) -> str:
        """解析日期字符串"""
        if not date_str:
            return ""
        
        # 常见RSS日期格式
        formats = [
            "%a, %d %b %Y %H:%M:%S %z",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%d %H:%M:%S"
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d %H:%M")
            except:
                continue
        
        return date_str[:20]  # 截断返回
    
    def _filter_by_date(self, items: List[Dict], days: int) -> List[Dict]:
        """按日期过滤"""
        cutoff = datetime.now() - timedelta(days=days)
        results = []
        
        for item in items:
            published = item.get("published", "")
            # 简化处理：如果是"近期"或"今天"等，直接保留
            if published in ["", "近期", "今天", "昨天"]:
                results.append(item)
                continue
            
            try:
                # 尝试解析日期
                item_date = datetime.strptime(published[:10], "%Y-%m-%d")
                if item_date >= cutoff:
                    results.append(item)
            except:
                # 无法解析，默认保留
                results.append(item)
        
        return results
    
    def _deduplicate(self, items: List[Dict]) -> List[Dict]:
        """去重"""
        seen = set()
        results = []
        
        for item in items:
            # 使用标题+URL作为唯一标识
            key = f"{item.get('title', '')[:50]}_{item.get('url', '')[:50]}"
            
            if key not in seen:
                seen.add(key)
                results.append(item)
        
        return results


if __name__ == "__main__":
    # 测试
    fetcher = ContentFetcher()
    
    # 测试RSS
    print("=== 测试 RSS ===")
    results = fetcher.fetch_from_rss("https://hnrss.org/newest", limit=3)
    for r in results[:2]:
        print(f"  {r['title'][:50]}...")
