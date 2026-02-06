#!/usr/bin/env python3
"""
钱包历史收益分析
地址: HeBqoXv2f297qQcxmfbN1MexXLwisC1FvqYcKDZB8kP8
"""

import requests
import json
from datetime import datetime

RPC_URL = "https://api.mainnet-beta.solana.com"
WALLET = "HeBqoXv2f297qQcxmfbN1MexXLwisC1FvqYcKDZB8kP8"

def get_wallet_history(wallet, limit=50):
    """获取钱包最近50笔交易"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [wallet, {"limit": limit}]
    }
    try:
        r = requests.post(RPC_URL, json=payload, timeout=15)
        return r.json().get("result", [])
    except Exception as e:
        print(f"Error: {e}")
        return []

def analyze_transaction(sig):
    """分析单笔交易详情"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [sig, {"encoding": "json", "maxSupportedTransactionVersion": 0}]
    }
    try:
        r = requests.post(RPC_URL, json=payload, timeout=10)
        result = r.json().get("result", {})
        if not result:
            return None
        
        meta = result.get("meta", {})
        logs = meta.get("logMessages", [])
        
        # 检测交易类型
        tx_type = "UNKNOWN"
        if any("initializeMint" in log for log in logs):
            tx_type = "TOKEN_CREATE"
        elif any("Transfer" in log for log in logs):
            tx_type = "TRANSFER"
        elif any("MintTo" in log for log in logs):
            tx_type = "MINT"
        
        return {
            "signature": sig[:30] + "...",
            "type": tx_type,
            "success": meta.get("err") is None,
            "fee": meta.get("fee", 0) / 1e9,
            "timestamp": result.get("blockTime")
        }
    except:
        return None

def calculate_smart_score(txs):
    """计算聪明钱包评分"""
    if not txs:
        return {"tier": "UNKNOWN", "score": 0}
    
    total = len(txs)
    successful = len([t for t in txs if t.get("success")])
    token_creates = len([t for t in txs if t.get("type") == "TOKEN_CREATE"])
    
    # 胜率
    win_rate = successful / total if total > 0 else 0
    
    # 分级逻辑
    if token_creates >= 3 and win_rate >= 0.8:
        tier = "T1"
    elif token_creates >= 1 and win_rate >= 0.6:
        tier = "T2"
    else:
        tier = "T3"
    
    return {
        "tier": tier,
        "total_txs": total,
        "successful": successful,
        "win_rate": win_rate,
        "token_creates": token_creates
    }

def main():
    print("="*70)
    print(f"🔍 钱包分析报告 | {datetime.now().strftime('%H:%M:%S')}")
    print("="*70)
    print(f"\n目标地址: {WALLET}")
    print(f"Solscan:  https://solscan.io/account/{WALLET}")
    
    print(f"\n📡 获取最近交易历史...")
    history = get_wallet_history(WALLET, limit=30)
    
    if not history:
        print("❌ 无法获取交易历史")
        return
    
    print(f"找到 {len(history)} 笔交易，分析中...")
    
    analyzed = []
    for i, tx in enumerate(history[:20]):  # 分析前20笔
        sig = tx.get("signature")
        details = analyze_transaction(sig)
        if details:
            analyzed.append(details)
    
    # 计算评分
    score = calculate_smart_score(analyzed)
    
    print("\n" + "-"*70)
    print("📊 交易统计")
    print("-"*70)
    print(f"总交易数:    {score['total_txs']}")
    print(f"成功交易:    {score['successful']}")
    print(f"胜率:        {score['win_rate']*100:.1f}%")
    print(f"发币次数:    {score['token_creates']}")
    
    print("\n" + "-"*70)
    print(f"🏆 分级结果: {score['tier']}")
    print("-"*70)
    
    if score['tier'] == "T1":
        print("评价: 高频发币 + 高胜率，核心关注对象")
    elif score['tier'] == "T2":
        print("评价: 有发币经验，胜率尚可，观察对象")
    elif score['tier'] == "T3":
        print("评价: 发币较少或胜率一般，谨慎跟单")
    else:
        print("评价: 数据不足，无法判断")
    
    print("\n" + "="*70)
    print("最近交易明细 (前10笔):")
    print("-"*70)
    for tx in analyzed[:10]:
        status = "✅" if tx['success'] else "❌"
        print(f"{status} {tx['type']:12} | {tx['signature']} | {tx['fee']:.4f} SOL")
    
    print("="*70)

if __name__ == "__main__":
    main()
