# Xiaoyuzhou Podcast Fetch SOP

## Overview
Xiaoyuzhou (xiaoyuzhoufm.com) is a Next.js SPA — all direct fetch methods fail. Use RSS feed approach instead.

## Steps

### 1. Find RSS URL (iTunes Search API, no proxy needed)
```bash
curl "https://itunes.apple.com/search?term=<podcast_name>&media=podcast&country=CN&limit=5" \
  | python3 -c "import json,sys; data=json.load(sys.stdin); [print(r['collectionName'],'->',r.get('feedUrl','N/A')) for r in data['results']]"
```

### 2. Download RSS XML (use HTTP_PROXY if needed)
```bash
curl ${HTTP_PROXY:+-x $HTTP_PROXY} -L "<feedUrl>" -o /tmp/pod_feed.xml
```

### 3. Parse Latest Episode
```python
import xml.etree.ElementTree as ET
tree = ET.parse("/tmp/pod_feed.xml")
channel = tree.getroot().find('channel')
latest = channel.findall('item')[0]
audio_url = latest.find('enclosure').get('url')
title = latest.find('title').text
```

### 4. Download Audio
```bash
curl ${HTTP_PROXY:+-x $HTTP_PROXY} -L "<audio_url>" -o /tmp/podcast.m4a --progress-bar
```

### 5. Transcribe (faster-whisper)
```python
from faster_whisper import WhisperModel
model = WhisperModel("small", device="cpu", compute_type="int8")
segments, info = model.transcribe("/tmp/podcast.m4a", language="zh", beam_size=5)
with open("/tmp/transcript.txt", "w") as f:
    for seg in segments: f.write(f"[{seg.start:.1f}s] {seg.text}\n")
```
⚠️ 80-minute audio ~15-30 min CPU time. Notify user before starting.

## Limitations
- Only podcasts with RSS feed (most Xiaoyuzhou podcasts have one)
- Transcription: CPU only, ~3-5x realtime (small model, int8)
- For AI features (summary/QA) → feed transcript to LLM
