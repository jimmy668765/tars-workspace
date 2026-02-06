#!/usr/bin/env python3
"""
聪明钱包发现与分级系统 v0.1
使用模拟数据演示完整流程
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict

# 模拟钱包数据
MOCK_WALLETS = [
    {
        "address": "93VysxDiDvaY5EMTVqN9JBho75DR2nA4tsXGxqrcTpdL",
        "trades_30d": 15,
        "win_rate": 0.75,
        "avg_return": 3.5,
        "max_return": 12.0,
        "early_entries": 5,  # 1小时内买入次数
        "tier": "T1"
    },
    {
        "address": "7nY7H11PB7q9t7wD5zQYjK1s7mV4g2NJK6pLxR9T5vA",
        "trades_30d": 25,
        "win_rate": 0.62,
        "avg_return": 2.1,
        "max_return": 8.5,
        "early_entries": 3,
        "tier": "T2"
    },
    {
        "address": "4xM8K22QN9qB7v5X9w6YjD2s8nW5h3MPL7oKxS8U6vB",
        "trades_30d": 40,
        "win_rate": 0.45,
        "avg_return": 1.8,
        "max_return": 25.0,  # 偶尔抓到大机会
        "early_entries": 2,
        "tier": "T3"
    }
]

def classify_wallet(wallet: Dict) -> str:
    """分级钱包"""
    if wallet["win_rate"] >= 0.70 and wallet["avg_return"] >= 3.0:
        return "T1"
    elif wallet["win_rate"] >= 0.50 and wallet["avg_return"] >= 1.5:
        return "T2"
    else:
        return "T3"

def check_alert_condition(wallets: List[Dict]) -> List[Dict]:
    """检查是否触发监控条件"""
    alerts = []
    
    # 模拟新币发射
    new_token = {
        "symbol": "MOON2026",
        "address": "MoonTokenAddress123",
        "market_cap": 50000,  # $50k
        "launch_time": datetime.now() - timedelta(minutes=30)
    }
    
    # 检查 T1 钱包买入情况
    t1_buyers = [w for w in wallets if w["tier"] == "T1"]
    
    if len(t1_buyers) >= 1:  # 实际应该是 >=3
        alerts.append({
            "type": "SMART_MONEY_ALERT",
            "token": new_token,
            "t1_buyers": len(t1_buyers),
            "recommendation": "HIGH_ATTENTION",
            "timestamp": datetime.now().isoformat()
        })
    
    return alerts

def generate_report():
    """生成每日报告"""
    print("=" * 50)
    print("聪明钱包监控报告")
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 分类统计
    t1_wallets = [w for w in MOCK_WALLETS if w["tier"] == "T1"]
    t2_wallets = [w for w in MOCK_WALLETS if w["tier"] == "T2"]
    t3_wallets = [w for w in MOCK_WALLETS if w["tier"] == "T3"]
    
    print(f"\n📊 钱包统计:")
    print(f"  Tier 1 (核心): {len(t1_wallets)} 个")
    print(f"  Tier 2 (观察): {len(t2_wallets)} 个")
    print(f"  Tier 3 (试验): {len(t3_wallets)} 个")
    
    print(f"\n🏆 Tier 1 钱包详情:")
    for w in t1_wallets:
        print(f"  • {w['address'][:20]}...")
        print(f"    胜率: {w['win_rate']*100:.0f}%, 平均收益: {w['avg_return']:.1f}x")
        print(f"    早期买入: {w['early_entries']} 次")
    
    # 检查警报
    alerts = check_alert_condition(MOCK_WALLETS)
    
    print(f"\n🚨 今日警报:")
    if alerts:
        for alert in alerts:
            print(f"  ⚠️ {alert['type']}")
            print(f"     Token: {alert['token']['symbol']}")
            print(f"     T1买家: {alert['t1_buyers']} 个")
            print(f"     建议: {alert['recommendation']}")
    else:
        print("  暂无异常")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    generate_report()
    
    # 保存到文件
    output = {
        "timestamp": datetime.now().isoformat(),
        "wallets": MOCK_WALLETS,
        "summary": {
            "t1_count": len([w for w in MOCK_WALLETS if w["tier"] == "T1"]),
            "t2_count": len([w for w in MOCK_WALLETS if w["tier"] == "T2"]),
            "t3_count": len([w for w in MOCK_WALLETS if w["tier"] == "T3"])
        }
    }
    
    with open("/tmp/smart_wallet_report.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("\n✅ 报告已保存到: /tmp/smart_wallet_report.json")
