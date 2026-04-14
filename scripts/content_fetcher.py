#!/usr/bin/env python3
"""
AI信息雷达 - 内容抓取器
抓取各大媒体最新内容

Tool priority:
  - Twitter: xreach (agent-reach) → guest token GraphQL fallback
  - Search: mcporter (Exa) → Jina Search API fallback → DuckDuckGo fallback
  - WeChat: agent-reach fetch → curl fallback
"""

import os
import subprocess
import shutil
import json
import re
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import feedparser
import requests
from bs4 import BeautifulSoup

# Check if agent-reach tools are available
HAS_XREACH = shutil.which("xreach") is not None
HAS_MCPORTER = shutil.which("mcporter") is not None
HAS_AGENT_REACH = shutil.which("agent-reach") is not None

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
            
            articles = []
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
        """从公众号抓取最新文章（通过搜狗微信搜索）
        Primary: agent-reach fetch → Fallback: curl
        """
        try:
            search_url = f"https://weixin.sogou.com/weixin?type=1&query={wechat_id}"
            content = ""
            
            # Primary: agent-reach fetch
            if HAS_AGENT_REACH:
                try:
                    result = subprocess.run(
                        ["agent-reach", "fetch", search_url],
                        capture_output=True, text=True, timeout=30
                    )
                    if result.stdout and len(result.stdout) > 100:
                        content = result.stdout
                except:
                    pass
            
            # Fallback: curl
            if not content:
                try:
                    result = subprocess.run(
                        ["curl", "-s", search_url],
                        capture_output=True, text=True, timeout=30
                    )
                    content = result.stdout
                except:
                    pass
            
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
        """从Twitter抓取最新推文
        Primary: xreach (agent-reach) → Fallback: guest token GraphQL API
        """
        # Primary: xreach
        if HAS_XREACH:
            try:
                result = subprocess.run(
                    ["xreach", "tweets", f"@{username}", "-n", str(limit), "--json"],
                    capture_output=True, text=True, timeout=30
                )
                if result.stdout and result.stdout.strip().startswith("["):
                    tweets = json.loads(result.stdout)
                    results = []
                    for tweet in tweets:
                        results.append({
                            "title": tweet.get("text", "")[:100] + "...",
                            "url": f"https://twitter.com/{username}/status/{tweet.get('id')}",
                            "summary": tweet.get("text", ""),
                            "published": tweet.get("created_at", ""),
                            "source": f"@{username}",
                            "tags": ["Twitter"]
                        })
                    if results:
                        return results
            except Exception as e:
                print(f"xreach twitter error: {e}")
        
        # Fallback: guest token GraphQL API (no login required)
        return self._fetch_twitter_graphql(username, limit)
    
    def _fetch_twitter_graphql(self, username: str, limit: int = 5) -> List[Dict]:
        """Fetch tweets via X/Twitter guest token GraphQL API (no login)."""
        BEARER = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
        UA = "TwitterAndroid/10.21.0-release.0 (310210000-r-0) ONEPLUS+A3010/9 (OnePlus;ONEPLUS+A3010;OnePlus;OnePlus3;0;;1;2016)"

        try:
            headers = {"Authorization": f"Bearer {BEARER}", "User-Agent": UA}
            proxy_url = os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")
            proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None

            r = requests.post(
                "https://api.twitter.com/1.1/guest/activate.json",
                headers=headers, proxies=proxies, timeout=15
            )
            guest_token = r.json()["guest_token"]

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
            print(f"Twitter GraphQL fallback error: {e}")
            return []
    
    def search_latest_content(self, keyword: str, days: int = 2, limit: int = 10) -> List[Dict]:
        """搜索关键词最新内容
        Primary: mcporter (Exa) → Fallback: Jina Search API → DuckDuckGo
        """
        results = []
        
        # 1. Primary: mcporter + Exa (agent-reach ecosystem)
        if HAS_MCPORTER:
            try:
                result = subprocess.run(
                    ["mcporter", "call",
                     f"exa.web_search_exa(query: '{keyword} AI news past {days} days', numResults: {limit})"],
                    capture_output=True, text=True, timeout=30
                )
                if result.stdout and result.stdout.strip().startswith("["):
                    search_results = json.loads(result.stdout)
                    for item in search_results:
                        results.append({
                            "title": item.get("title", ""),
                            "url": item.get("url", ""),
                            "summary": item.get("text", "")[:200],
                            "published": "近期",
                            "source": item.get("source", "Exa"),
                            "tags": [keyword]
                        })
                    if results:
                        return results[:limit]
            except Exception as e:
                print(f"mcporter/Exa search error: {e}")
        
        # 2. Fallback: Jina Search API (free, no API key)
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
                    "source": item.get("url", "").split("/")[2] if item.get("url") else "Jina",
                    "tags": [keyword]
                })
            if results:
                return results[:limit]
        except Exception as e:
            print(f"Jina search error: {e}")

        # 3. Last fallback: DuckDuckGo HTML search
        try:
            proxy_url = os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")
            proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
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
        
        if media_config.get("rss"):
            results = self.fetch_from_rss(media_config["rss"], limit=5)
        elif media_config.get("website"):
            results = self.fetch_from_website(media_config["website"], limit=5)
        elif media_config.get("twitter"):
            results = self.fetch_from_twitter(media_config["twitter"], limit=5)
        elif media_config.get("wechat"):
            results = self.fetch_from_wechat(media_config["wechat"], limit=5)
        
        if days > 0:
            results = self._filter_by_date(results, days)
        
        for item in results:
            item["media_id"] = media_id
            item["media_name"] = media_config.get("name", "")
        
        return results
    
    def fetch_topic_content(self, topic: str, db, limit: int = 10) -> List[Dict]:
        """获取主题相关内容"""
        keywords = db.get_keywords(topic)
        resources = db.get_resources_by_focus(topic)
        
        all_content = []
        for resource in resources[:5]:
            if resource.get("rss") or resource.get("website") or resource.get("twitter"):
                content = self.fetch_media_latest(
                    resource.get("id", ""),
                    resource,
                    days=2
                )
                all_content.extend(content)
        
        search_results = self.search_latest_content(topic, days=2, limit=limit)
        all_content.extend(search_results)
        all_content = self._deduplicate(all_content)
        
        return all_content[:limit]
    
    def _parse_date(self, date_str: str) -> str:
        """解析日期字符串"""
        if not date_str:
            return ""
        
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
        
        return date_str[:20]
    
    def _filter_by_date(self, items: List[Dict], days: int) -> List[Dict]:
        """按日期过滤"""
        cutoff = datetime.now() - timedelta(days=days)
        results = []
        
        for item in items:
            published = item.get("published", "")
            if published in ["", "近期", "今天", "昨天", "Recent"]:
                results.append(item)
                continue
            
            try:
                item_date = datetime.strptime(published[:10], "%Y-%m-%d")
                if item_date >= cutoff:
                    results.append(item)
            except:
                results.append(item)
        
        return results
    
    def _deduplicate(self, items: List[Dict]) -> List[Dict]:
        """去重"""
        seen = set()
        results = []
        
        for item in items:
            key = f"{item.get('title', '')[:50]}_{item.get('url', '')[:50]}"
            if key not in seen:
                seen.add(key)
                results.append(item)
        
        return results


if __name__ == "__main__":
    fetcher = ContentFetcher()
    
    print("=== 测试 RSS ===")
    results = fetcher.fetch_from_rss("https://hnrss.org/newest", limit=3)
    for r in results[:2]:
        print(f"  {r['title'][:50]}...")
