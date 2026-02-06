#!/bin/bash
# DEX Screener Smart Wallet Discovery
# 自动发现聪明钱包并分类

API_URL="https://api.dexscreener.com/latest/dex/pairs/solana"
OUTPUT_FILE="/home/ubuntu/.openclaw/workspace/data/smart_wallets_$(date +%Y%m%d).json"

# 创建数据目录
mkdir -p /home/ubuntu/.openclaw/workspace/data

# 获取 Solana 新币对数据
echo "Fetching DEX Screener data..."
curl -s "$API_URL" | jq '.pairs[:100]' > /tmp/dex_pairs.json

# 筛选条件：
# 1. 市值 < $100k
# 2. 24h 交易量 > $10k
# 3. 24h 价格变化 > 50%
# 4. 有早期买入标记

echo "Filtering high-potential tokens..."
jq '[.[] | select(
  (.marketCap | tonumber) < 100000 and
  (.volume.h24 | tonumber) > 10000 and
  (.priceChange.h24 | tonumber) > 50
)]' /tmp/dex_pairs.json > "$OUTPUT_FILE"

# 提取钱包地址（从交易记录中）
echo "Extracting wallet addresses..."
jq -r '.[].txns | keys[]' "$OUTPUT_FILE" 2>/dev/null | sort | uniq > /tmp/potential_wallets.txt

echo "Found $(wc -l < /tmp/potential_wallets.txt) potential wallets"
echo "Data saved to: $OUTPUT_FILE"
