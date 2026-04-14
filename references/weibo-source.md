# 微博数据源 — 国内 AI 大V动态

## 用途
当用户要求获取国内 AI 领域大V（如贾扬清、Andrej Karpathy 中文账号等）的微博动态时使用。

## 抓取 SOP

1. **定位用户微博 UID**
   - catclaw-search：`"@用户名 site:weibo.com"` 或直接搜 `用户名 weibo`
   - 从结果 URL 提取 UID（格式：`weibo.com/u/<UID>`）

2. **获取最近帖子**
   - 方案A：catclaw-search `site:weibo.com/u/<UID>` 搜索近期帖子 URL
   - 方案B：agent-browser open `https://weibo.com/u/<UID>`，visitor cookie 自动获取，抓取页面帖子列表

3. **读取单条帖子正文**
   - agent-browser 打开帖子 URL
   - CSS selector：`.detail_wbtext_4CRf9`
   - 备选：页面时间戳前后文本块

## 已知 AI 大V 微博账号（可按需补充）
| 姓名 | 微博 | 备注 |
|------|------|------|
| 贾扬清 | @贾扬清 | PyTorch/Caffe 作者 |
| 吴恩达（中文） | @吴恩达AndrewNg | 英文主账号在 X |

## 限制
- 未登录只能看公开帖子
- 图片/视频帖子只能获取文本
- 搜索排序非严格时间序
