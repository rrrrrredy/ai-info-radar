---
name: ai-info-radar
description: "AI news and resource discovery with subscription push. Triggers: AI media recommendations, AI podcasts, AI books, AI news, AI video recommendations, set up push notifications, subscribe to AI news, AI daily digest, scheduled AI push, Weibo AI influencers, latest from Jiqizhixin. Not for: real-time search; non-AI media."
tags: [ai, media, radar, news, podcast, book]
---

# AI Information Radar V8

## First Use

Run the dependency check script before first use:
```bash
bash scripts/setup.sh
```
> The agent will auto-run this on first trigger; usually no manual action needed.

**Your all-in-one AI news assistant** — aggregates 50+ AI media, blogs, podcasts, and book resources. Supports latest content fetching, smart recommendations, and scheduled push notifications.

---

## Feature Overview

| Feature | Description | Trigger Words |
|:---|:---|:---|
| **Resource Database** | Query all AI learning resources | `AI media`, `AI podcasts`, `AI books`, `AI videos` |
| **Latest Content** | Fetch newest articles from sources | `What did Jiqizhixin post recently`, `Search latest on OpenAI` |
| **Smart Recommendations** | Recommend based on user background | `AI resources for beginners`, `Technical AI resources` |
| **Bookmark Management** | Track read/favorite items | `Bookmark this`, `My AI reading list`, `My bookmarks` |
| **Scheduled Push** | Custom frequency + topic notifications | `Set up hourly Agent news push` |

---

## Trigger Words

### Resource Queries
- `AI媒体推荐`, `推荐AI公众号`, `AI播客有哪些`
- `AI书籍推荐`, `学AI看什么书`
- `AI视频推荐`, `AI课程推荐`

### Latest Content
- `{media_name}最近发了什么` — e.g., What did Jiqizhixin post recently
- `搜 {keyword} 最新` — e.g., Search latest on Agent
- `{media_name} 最新文章`

### Smart Recommendations
- `适合小白的AI资源`, `AI入门推荐`
- `技术向AI媒体`, `产品向AI资讯`
- `英文AI资源`, `中文AI资源`

### Bookmark Management
- `收藏这个`, `加入收藏`
- `我的收藏`, `我的AI书单`
- `取消收藏 {resource_name}`

### Scheduled Push
- `设置 {frequency} 推送 {topic}` — e.g., Set up hourly Agent news push
- `设置推送`, `订阅AI资讯`, `每天推送AI资讯`, `设置AI日报`
- `查看我的推送设置`
- `取消推送 {topic}`
- `修改推送频率为 {frequency}`

---

## Supported Resources

### Chinese Media / WeChat Accounts
Jiqizhixin (机器之心), Liangziwei (量子位), InfoQ AI, CSDN AI, AI前线, 新智元, AI科技评论, DataFunTalk, AI大模型实验室, 赛博禅心, BAAI (智源研究院), Mila Forum, AI研习社

### Twitter/X
Fei-Fei Li, Andrej Karpathy, Yann LeCun, Mu Li, Lin Junyang, Dai Yusen, Baoyu, Guicang, swyx, Greg Brockman, Sam Altman, Demis Hassabis

### Blogs / Websites
LessWrong, Import AI, The Batch, Papers With Code, Hugging Face Blog, Google AI Blog, OpenAI Blog, Anthropic Blog, Gradient Flow, Weights & Biases

### Podcasts
42章经, 硅谷101, AI局内人, Latent Space, The TWIML AI Podcast, Lex Fridman Podcast

### Books
Deep Learning (Goodfellow), Dive into Deep Learning (Li Mu), AIMA (Russell & Norvig), Life 3.0 (Tegmark), AI Superpowers (Kai-Fu Lee), Human Compatible (Russell)

### Videos / Courses
Hung-Yi Lee ML, Andrew Ng Deep Learning, Mu Li Dive into DL, Andrej Karpathy Neural Networks, 3Blue1Brown, Two Minute Papers

---

## Execution Flow

### Step 1: Determine User Intent
- Query resource list → Return matching category content directly (no fetching needed)
- Fetch latest content → Enter Step 2
- Smart recommendation → Ask user background then recommend
- Bookmark management → Read/write `~/.ai-info-radar/favorites.json`
- **Set up push / Subscribe to AI news / Set up daily digest** → Enter "Subscription + Push Flow (V3)"

### Step 2: Fetch Latest Content

Select tools by platform type:

| Platform | Primary Tool | Fallback Tool |
|---------|---------|---------|
| WeChat Accounts | agent-reach fetch / Camoufox + HTTP proxy | Web search engines |
| Twitter/X | xreach (agent-reach) → `x_scraper.py` (guest token fallback) | Web search fallback |
| Weibo | Web search to locate UID/post URL + Playwright (visitor cookie) | — |
| Blogs/Websites | xread (agent-reach) → `web_fetch` / `r.jina.ai` | web_search |
| Bilibili/YouTube | yt-dlp / platform API | web_search |
| Content Search | mcporter/Exa (agent-reach) → Jina Search API (free) | DuckDuckGo HTML |
| Podcasts | iTunes Search API → RSS → download XML → parse latest episode | faster-whisper local transcription |

> 📌 **Xiaoyuzhou Podcasts**: Use iTunes Search API to get RSS → download XML → parse latest episode. See `references/podcast-xiaoyuzhou.md`.

> ⚠️ WeChat Official Accounts may require HTTP proxy (`HTTP_PROXY` env var) in environments where direct access is blocked.

> 📌 **Weibo**: Chinese AI influencers (e.g., Jia Yangqing, Andrew Ng Chinese account) tracked via web search to locate UID/post URLs, then Playwright with visitor cookie for content. Text selector: `.detail_wbtext_4CRf9`. See `references/weibo-source.md`.

**Twitter/X Fetch Example:**
```bash
# Check AI researchers' latest tweets (top 10)
python3 scripts/x_scraper.py timeline karpathy --count 10
python3 scripts/x_scraper.py timeline ylecun --count 10
# Get user full profile (with follower count)
python3 scripts/x_scraper.py profile _LuoFuli --json
```

### Step 3: Content Processing & Output

After fetching, automatically:
- Deduplicate (same article across platforms, by URL + title similarity)
- Generate summaries (long articles compressed to 3-5 key points)
- Card format output (see format below)

---

## Subscription + Push Flow (V3)

### First-Time Push Setup

When user says "set up push", "subscribe to AI news", "daily AI digest":

**Step 1: Ask for Configuration**
- Focus area? (technical / product / general)
- Push frequency? (daily / weekly / real-time)
- Push time? (default 09:00)

**Step 2: Write Config File**

Path: `~/.ai-info-radar/push-config.json`

```json
{
  "focus": "technical",
  "sources": ["Jiqizhixin", "Liangziwei", "Andrej Karpathy", "Lex Fridman Podcast"],
  "push_time": "09:00",
  "frequency": "daily"
}
```

**Step 3: Configure Cron (⚠️ Use UTC time; Beijing 09:00 = UTC 01:00)**

```bash
# Example: configure your cron scheduler to run at UTC 01:00 daily
# The job should: read ai-info-radar push config, fetch latest content, format as daily digest, send to user
```

**Step 4: Add heartbeat fallback**

Configure a fallback check: if current time is 08:45-09:30 and today's digest hasn't been sent, trigger immediately.

### Fetch Execution Logic

When triggered:
1. Read `~/.ai-info-radar/push-config.json`
2. For each subscribed source, fetch latest content using appropriate tools
3. Filter: only content from past 24 hours
4. Format as daily digest (title + one-line summary + link)
5. Limit to 10 items max to avoid excessive length
6. Send to user via configured channel

### Daily Digest Format

```
🤖 AI Daily Digest · {date}

📰 Today's Picks ({N} items):

1. **{title}**
   Source: {media} | {time}
   Summary: {one-liner}
   🔗 {link}

...

💡 Today's Highlight: {most important item}
```

---

## Scheduled Push Configuration

### Frequency Options
- `Hourly`, `Every 3 hours`, `Every 6 hours`
- `Daily 9 AM`, `Daily 6 PM`
- `Monday`, `Friday`

### Topic Options
- `All`, `Agent`, `LLM`, `Multimodal`
- `AI Safety`, `AI Products`, `AI Engineering`, `AI Startups`

### Count Options
- Per push: `1 item`, `3 items`, `5 items`

### Cron Configuration (⚠️ UTC Conversion)

```bash
# Example: Daily 9 AM push for Agent news, 3 items each time
# Note: cron uses UTC time. Beijing 09:00 = UTC 01:00
# Schedule: "0 1 * * *" → "Fetch latest Agent news and push to user, 3 items"
```

> ⚠️ **UTC Conversion Reminder**: Beijing time - 8h = UTC time.
> E.g., Beijing 09:00 → UTC 01:00, Beijing 18:00 → UTC 10:00.

### Config Storage (V3)

User push config saved in `~/.ai-info-radar/push-config.json`:
- Shareable across sessions
- Manually editable
- Import/export supported

---

## Output Format

**Card-style output**, each item contains:

```
📰 [Media Name] · ⏱️ Published Time
🏷️ Content Tags
📝 Article Title
Summary (2-3 lines)
🔗 Original Link
```

---

## Error Handling

| Error Scenario | Handling |
|---------|---------|
| WeChat fetch failed (proxy issue) | Auto-fallback to web search, notify "content from third-party aggregation" |
| Twitter/X fetch failed | Retry with `x_scraper.py timeline <handle>`; after 3 consecutive failures, notify user |
| Website RSS broken | Switch to web_fetch for homepage article list |
| Push job failed | Add heartbeat fallback trigger rule |

---

### Gotchas

⚠️ WeChat Official Accounts may be blocked from direct access → Set `HTTP_PROXY` environment variable if needed

⚠️ Twitter/X **no auth-token needed** → `x_scraper.py` + guest token provides login-free profile and timeline; **search is still limited** (guest token SearchTimeline returns empty)

⚠️ RSS source becomes invalid → First try web_fetch for homepage articles, then fallback to web search

⚠️ Cron uses UTC time — don't enter Beijing time directly. Beijing -8h = UTC

⚠️ Cron push fails silently → Add heartbeat fallback to ensure daily digest isn't missed

⚠️ `feedparser` not pre-installed → Run `pip install feedparser` before first use

---

### Hard Stop

**If the same tool call fails more than 3 times, stop immediately.** List all failed approaches and reasons, mark **"Manual intervention required"**, and wait for user confirmation.

---

## Dependencies

- Python 3.8+ (usually pre-installed)
- `feedparser`: `pip install feedparser` (RSS parsing; auto-prompted on first use)
- `requests`: `pip install requests` (usually pre-installed)

### Recommended: agent-reach (enhanced search & fetch)

`agent-reach` provides superior multi-platform search (xreach), content extraction (xread), and API wrappers (mcporter/Exa). Without it, the skill falls back to Jina Search API and guest token GraphQL.

**Install (choose one):**
```bash
# Option 1: pip (recommended)
pip install agent-reach
agent-reach install --env=auto --safe

# Option 2: ClawHub
npx clawhub install agent-reach
```

After installation, run `agent-reach doctor` to verify. Optional: `npm i -g mcporter && mcporter config add exa https://mcp.exa.ai/mcp` for Exa semantic search.

> Without agent-reach, the skill auto-falls back to Jina Search API + guest token GraphQL — still functional for most use cases.

---

## Changelog

### V8 (2026-04-08)
- Added Xiaoyuzhou podcast SOP (iTunes RSS + faster-whisper), new `references/podcast-xiaoyuzhou.md`
- Added podcast row in Step 2 tool table

### V7 (2026-04-08)
- Added Weibo as data source: Chinese AI influencer tracking via web search + Playwright (visitor cookie)
- New `references/weibo-source.md` (scraping SOP + known AI influencer accounts)

### V6 (2026-04-08)
- Integrated X/Twitter login-free scraping: `x_scraper.py` (guest token, no auth-token needed)

### V5 (2026-04-08)
- Cleaned up description triggers, removed unrelated entries
- New `references/resource-list.md`

### V3 (2026-04-08)
- Upgraded to real subscription + scheduled push system (cron-driven, auto content fetching)
- New "Subscription + Push Flow" section

### V2 (2026-04-07)
- Added execution flow (Step 1-3), platform tool selection and fallback rules
- Added error handling table

### V1 (Initial)
- Resource query, content fetching, smart recommendations, bookmarks, scheduled push
- 50+ AI media/blog/podcast/book resources aggregated
