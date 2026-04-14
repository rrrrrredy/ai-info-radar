# Weibo AI Influencer Source

## Scraping SOP

### Step 1: Locate User UID
- Web search: `"@username site:weibo.com"` or `"username weibo"`
- Extract UID from URL: `weibo.com/u/<UID>`

### Step 2: Get Recent Posts
- Approach A: Web search `site:weibo.com/u/<UID>` for recent post URLs
- Approach B: Playwright → open `https://weibo.com/u/<UID>` → visitor cookie auto-set → scrape post list

### Step 3: Read Post Content
- Playwright → open post URL
- Text selector: `.detail_wbtext_4CRf9`
- Fallback: extract text near timestamp elements

### Step 4: Output
- Format: `[author] [time] [content] [link]`

## Known AI Influencers on Weibo
| Name | Weibo ID | Focus |
|------|---------|-------|
| 贾扬清 (Yangqing Jia) | jiayangqing | AI Infra / CEO |
| 李沐 (Mu Li) | limu | Deep Learning / Education |

## Limitations
- Only public posts (followers-only content not accessible)
- Media files viewable but not directly downloadable
- Timeline accuracy depends on search engine ordering
