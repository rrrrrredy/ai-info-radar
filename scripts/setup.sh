#!/usr/bin/env bash
# setup.sh - 首次使用依赖检测与安装
# Usage: bash scripts/setup.sh

set -e

echo "🔍 检测依赖..."

MISSING=0

if ! python3 -c "import feedparser" 2>/dev/null; then
  echo "📦 安装 feedparser..."
  pip install -q feedparser
  MISSING=1
fi

if ! python3 -c "import requests" 2>/dev/null; then
  echo "📦 安装 requests..."
  pip install -q requests
  MISSING=1
fi

if ! python3 -c "import fuzzywuzzy" 2>/dev/null; then
  echo "📦 安装 fuzzywuzzy..."
  pip install -q fuzzywuzzy python-Levenshtein
  MISSING=1
fi

if ! python3 -c "import bs4" 2>/dev/null; then
  echo "📦 安装 beautifulsoup4..."
  pip install -q beautifulsoup4
  MISSING=1
fi

if [ "$MISSING" -eq 0 ]; then
  echo "✅ 所有依赖已就绪"
else
  echo "✅ 依赖安装完成"
fi

# 最终验证
python3 -c "import feedparser; print('验证通过: feedparser')"
python3 -c "import requests; print('验证通过: requests')"
python3 -c "import fuzzywuzzy; print('验证通过: fuzzywuzzy')"
python3 -c "import bs4; print('验证通过: beautifulsoup4')"
echo "🎉 setup 完成，可以正常使用"
