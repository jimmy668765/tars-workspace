#!/usr/bin/env python3
"""
DexScreener 聪明钱包监控系统
无需 API key，直接调用公开接口
"""

import requests
import json
import time
from datetime import datetime, timedelta

# 监控配置
CONFIG = {
    "min_market_cap": 1000,      # 最小市值 $1K
    "max_market_cap": 100000,    # 最大市值 $100K
    "min_liquidity": 2000,       # 最小流动性 $2K
    "min_buy_ratio": 2.0,        # 买入/卖出比例 > 2:1
    "chains": ["solana", "ethereum", "bsc"],  # 重点监控链
}

def get_new_pairs(chain="solana", limit=50):
    """获取新币对 - 使用搜索API获取热门交易对"""
    # 搜索该链上最近活跃的交易对
    url = f"https://api.dexscreener.com/latest/dex/search?q={chain}"
    try:
        resp = requests.get(url, timeout=30)
        data = resp.json() if resp.status_code == 200 else {}
        pairs = data.get("pairs", [])
        # 只返回该链的数据
        return [p for p in pairs if p.get("chainId") == chain][:limit]
    except Exception as e:
        print(f"Error fetching pairs: {e}")
        return []

def analyze_pair(pair):
    """分析交易对"""
    try:
        market_cap = pair.get("marketCap", 0)
        liquidity = pair.get("liquidity", {}).get("usd", 0)
        
        # 市值筛选
        if not (CONFIG["min_market_cap"] <= market_cap <= CONFIG["max_market_cap"]):
            return None
            
        if liquidity < CONFIG["min_liquidity"]:
            return None
        
        txns = pair.get("txns", {})
        h24 = txns.get("h24", {})
        buys = h24.get("buys", 0)
        sells = h24.get("sells", 0)
        
        # 买入比例
        buy_ratio = buys / max(sells, 1)
        if buy_ratio < CONFIG["min_buy_ratio"]:
            return None
        
        return {
            "symbol": pair.get("baseToken", {}).get("symbol", "Unknown"),
            "name": pair.get("baseToken", {}).get("name", "Unknown"),
            "address": pair.get("baseToken", {}).get("address", ""),
            "chain": pair.get("chainId", ""),
            "dex": pair.get("dexId", ""),
            "market_cap": market_cap,
            "liquidity": liquidity,
            "price_usd": pair.get("priceUsd", 0),
            "price_change_24h": pair.get("priceChange", {}).get("h24", 0),
            "buys_24h": buys,
            "sells_24h": sells,
            "buy_ratio": round(buy_ratio, 2),
            "volume_24h": pair.get("volume", {}).get("h24", 0),
            "url": pair.get("url", ""),
        }
    except Exception as e:
        return None

def find_smart_wallets(token_address, chain="solana"):
    """
    识别聪明钱包 - 通过交易模式分析
    注意：DexScreener 不直接提供钱包数据，需要链上分析
    """
    # 这里可以集成 Helius/Alchemy API 进一步分析
    # 目前先做基础筛选
    return []

def scan_opportunities():
    """扫描机会"""
    results = []
    
    for chain in CONFIG["chains"]:
        print(f"\n🔍 扫描 {chain.upper()}...")
        pairs = get_new_pairs(chain, limit=100)
        
        for pair in pairs:
            analysis = analyze_pair(pair)
            if analysis:
                results.append(analysis)
                print(f"  ✅ {analysis['symbol']} | 市值: ${analysis['market_cap']:,.0f} | 买/卖: {analysis['buy_ratio']}")
    
    # 按市值排序
    results.sort(key=lambda x: x["market_cap"])
    return results

def generate_report(opportunities):
    """生成报告"""
    if not opportunities:
        return "未发现符合条件的标的"
    
    report = f"""
🚨 DexScreener 监控报告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}

发现 {len(opportunities)} 个潜在标的：

"""
    for i, opp in enumerate(opportunities[:10], 1):  # 只显示前10
        report += f"""
{i}. {opp['symbol']} ({opp['name']})
   合约地址: {opp['address'][:20]}...
   链: {opp['chain']} | DEX: {opp['dex']}
   市值: ${opp['market_cap']:,.0f} | 流动性: ${opp['liquidity']:,.0f}
   价格: ${float(opp['price_usd']):.8f} | 24h变化: {opp['price_change_24h']}%
   买入: {opp['buys_24h']} | 卖出: {opp['sells_24h']} | 比例: {opp['buy_ratio']}
   24h成交量: ${opp['volume_24h']:,.0f}
   链接: {opp['url']}
"""
    
    return report

if __name__ == "__main__":
    print("🚀 启动 DexScreener 聪明钱包监控系统...")
    opportunities = scan_opportunities()
    report = generate_report(opportunities)
    print(report)
    
    # 保存结果
    with open(f"/home/ubuntu/.openclaw/workspace/reports/dexscan_{datetime.now().strftime('%Y%m%d_%H%M')}.json", "w") as f:
        json.dump(opportunities, f, indent=2)
    
    print(f"\n📁 详细数据已保存到 reports/ 目录")
