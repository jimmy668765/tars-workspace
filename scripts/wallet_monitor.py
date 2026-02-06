#!/usr/bin/env python3
"""
聪明钱包监控系统 v0.1
监控指定钱包的交易活动
"""

import requests
import json
from datetime import datetime

RPC_URL = "https://api.mainnet-beta.solana.com"

# 待监控的钱包列表（等你给我）
WATCH_LIST = [
    # 示例格式:
    # {"address": "xxx", "tier": "T1", "label": "聪明钱包1"}
]

def get_wallet_transactions(wallet_address, limit=10):
    """获取钱包最近交易"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [wallet_address, {"limit": limit}]
    }
    try:
        r = requests.post(RPC_URL, json=payload, timeout=10)
        return r.json().get("result", [])
    except Exception as e:
        print(f"Error: {e}")
        return []

def analyze_transaction(signature):
    """分析单个交易"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [signature, {"encoding": "json", "maxSupportedTransactionVersion": 0}]
    }
    try:
        r = requests.post(RPC_URL, json=payload, timeout=10)
        tx_data = r.json().get("result", {})
        
        # 简化分析：检查是否是 Token 交易
        meta = tx_data.get("meta", {})
        log_messages = meta.get("logMessages", [])
        
        for log in log_messages:
            if "Transfer" in log or "MintTo" in log:
                return {
                    "type": "TOKEN_ACTIVITY",
                    "signature": signature[:20] + "...",
                    "timestamp": tx_data.get("blockTime")
                }
        return None
    except:
        return None

def monitor_wallets():
    """主监控函数"""
    print("="*60)
    print(f"🔍 聪明钱包监控 | {datetime.now().strftime('%H:%M')}")
    print("="*60)
    
    if not WATCH_LIST:
        print("\n⚠️ 监控列表为空")
        print("需要你给我聪明钱包地址才能启动监控")
        print("\n格式要求:")
        print('  {"address": "xxx", "tier": "T1", "label": "名字"}')
        return
    
    for wallet in WATCH_LIST:
        addr = wallet["address"]
        tier = wallet.get("tier", "?")
        label = wallet.get("label", "Unknown")
        
        print(f"\n[{tier}] {label}")
        print(f"  地址: {addr[:20]}...")
        
        txs = get_wallet_transactions(addr, limit=5)
        if txs:
            print(f"  最近交易: {len(txs)} 笔")
            for tx in txs[:3]:  # 只看前3笔
                sig = tx.get("signature", "")
                analysis = analyze_transaction(sig)
                if analysis:
                    print(f"    🔔 {analysis['type']}: {analysis['signature']}")
        else:
            print("  暂无交易或无法获取")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    monitor_wallets()
