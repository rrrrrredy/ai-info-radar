# 🤖 AI Information Radar

**Your all-in-one AI news assistant** — aggregates 50+ AI media, blogs, podcasts, and book resources. Supports latest content fetching, smart recommendations, and scheduled push notifications.

## Features

| Feature | Description |
|---|---|
| 📚 Resource Database | Query 50+ curated AI learning resources |
| 📰 Latest Content | Fetch newest articles from any tracked source |
| 🎯 Smart Recommendations | Personalized recommendations based on skill level |
| 💾 Bookmarks | Save and organize interesting content |
| ⏰ Scheduled Push | Custom frequency + topic daily/weekly digests |

## Quick Start

```bash
# Install dependencies
bash scripts/setup.sh

# Run
python3 scripts/ai_info_radar.py "AI媒体推荐"
python3 scripts/ai_info_radar.py "适合小白的AI资源"
python3 scripts/ai_info_radar.py "搜 Agent"
```

## Dependencies

- Python 3.8+
- `feedparser` (RSS parsing)
- `requests` (HTTP)
- `fuzzywuzzy` (fuzzy matching)
- `beautifulsoup4` (HTML parsing)

## Supported Sources

- **Chinese Media**: Jiqizhixin, Liangziwei, InfoQ AI, CSDN AI, Xinzhiyuan, DataFunTalk, and more
- **Twitter/X**: Fei-Fei Li, Andrej Karpathy, Yann LeCun, Sam Altman, and more
- **Blogs**: LessWrong, Import AI, The Batch, Papers With Code, Hugging Face, OpenAI, Anthropic
- **Podcasts**: 42章经, 硅谷101, Latent Space, Lex Fridman, TWIML AI
- **Books**: Deep Learning, Dive into DL, Life 3.0, AI Superpowers, AIMA
- **Videos**: Hung-Yi Lee ML, Andrew Ng DL, Karpathy NN, 3Blue1Brown

## Structure

```
ai-info-radar/
├── SKILL.md                         # Full skill documentation
├── README.md                        # This file
├── config/
│   └── default_schedule.json        # Default schedule configuration
├── data/
│   └── resources.json               # Complete resource database
├── references/
│   ├── resource-list.md             # Resource overview
│   ├── podcast-xiaoyuzhou.md        # Xiaoyuzhou podcast SOP
│   └── weibo-source.md             # Weibo scraping SOP
└── scripts/
    ├── setup.sh                     # Dependency installer
    ├── ai_info_radar.py             # Main entry point
    ├── resource_db.py               # Resource database manager
    ├── content_fetcher.py           # Content fetcher
    ├── card_formatter.py            # Output formatter
    ├── bookmark_manager.py          # Bookmark manager
    └── schedule_manager.py          # Schedule manager
```

## License

MIT
