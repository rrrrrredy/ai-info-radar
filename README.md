# ai-info-radar

AI news and media discovery assistant with subscription push — aggregates 50+ sources across media, blogs, podcasts, and books.

> OpenClaw Skill — works with [OpenClaw](https://github.com/openclaw/openclaw) AI agents

## What It Does

Your all-in-one AI news assistant. Aggregates 50+ AI media sources including WeChat Official Accounts, Twitter/X, Weibo, blogs, podcasts, and YouTube channels. Supports real-time content fetching, smart recommendations based on user background, bookmark management, and scheduled daily digest push via cron. Uses a multi-tool fallback strategy: agent-reach → Jina Search API → guest token GraphQL → web search.

## Quick Start

```bash
# Install via ClawHub (recommended)
openclaw skill install ai-info-radar

# Or clone this repo into your skills directory
git clone https://github.com/rrrrrredy/ai-info-radar.git ~/.openclaw/skills/ai-info-radar

# Install dependencies
bash scripts/setup.sh
```

## Features

- **50+ curated AI sources**: Chinese media (Jiqizhixin, Liangziwei, InfoQ AI), Twitter/X (Karpathy, LeCun, Sam Altman), blogs (LessWrong, OpenAI Blog, Anthropic Blog), podcasts (Latent Space, Lex Fridman), and more
- **Latest content fetching**: Platform-aware tool selection — WeChat (Camoufox + proxy), Twitter/X (guest token), Weibo (Playwright visitor cookie), blogs (RSS/web_fetch), podcasts (iTunes RSS + faster-whisper)
- **Smart recommendations**: Recommends resources based on user background (beginner/technical/product, Chinese/English)
- **Bookmark management**: Track read/favorite items in `~/.ai-info-radar/favorites.json`
- **Scheduled daily digest**: Cron-driven subscription push with configurable frequency, topic, and source filters
- **Card-format output**: Clean, structured output with media name, tags, summary, and original link
- **Multi-layer fallback**: Each platform has primary + fallback fetching strategies for resilience

## Usage

```
"AI媒体推荐"                    → Browse curated resource database
"机器之心最近发了什么"            → Fetch latest from Jiqizhixin
"搜 Agent 最新"                 → Search latest Agent news across sources
"适合小白的AI资源"               → Smart recommendation for beginners
"收藏这个"                      → Add to bookmarks
"设置每天9点推送AI资讯"           → Configure daily digest cron
"查看我的推送设置"               → Show current push configuration
```

## Project Structure

```
ai-info-radar/
├── SKILL.md                  # Main skill definition
├── scripts/
│   ├── setup.sh              # Dependency installer
│   ├── ai_info_radar.py      # Main radar logic
│   ├── bookmark_manager.py   # Bookmark CRUD
│   ├── card_formatter.py     # Card-style output formatter
│   ├── content_fetcher.py    # Multi-platform content fetcher
│   ├── resource_db.py        # Resource database queries
│   └── schedule_manager.py   # Push schedule management
├── references/
│   ├── podcast-xiaoyuzhou.md  # Xiaoyuzhou podcast SOP
│   ├── resource-list.md       # Full resource catalog
│   └── weibo-source.md        # Weibo scraping SOP
├── config/
│   └── default_schedule.json  # Push schedule configuration
├── data/
│   └── resources.json         # Resource database
└── .gitignore
```

## Requirements

- [OpenClaw](https://github.com/openclaw/openclaw) agent runtime
- Python 3.8+
- `feedparser` (RSS parsing)
- `requests` (HTTP calls)
- Optional: `agent-reach` for enhanced multi-platform search and fetch
- Optional: HTTP proxy for WeChat Official Account access

## License

[MIT](LICENSE)
