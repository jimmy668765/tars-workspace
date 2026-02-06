#!/usr/bin/env python3
"""
Solana 新币发射实时监控
直接通过 RPC 获取，无需 API Key
"""

import requests
import json
from datetime import datetime

RPC_URL = "https://api.mainnet-beta.solana.com"

def get_latest_slot():
    """获取最新区块高度"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSlot"
    }
    try:
        r = requests.post(RPC_URL, json=payload, timeout=10)
        return r.json()["result"]
    except:
        return None

def get_block(slot):
    """获取区块详情"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBlock",
        "params": [slot, {"encoding": "json", "maxSupportedTransactionVersion": 0}]
    }
    try:
        r = requests.post(RPC_URL, json=payload, timeout=10)
        return r.json().get("result")
    except:
        return None

def detect_new_tokens(block_data):
    """检测新币发射"""
    if not block_data or "transactions" not in block_data:
        return []
    
    new_tokens = []
    for tx in block_data["transactions"]:
        # 查找 createAccount + initializeMint 组合
        meta = tx.get("meta", {})
        if meta.get("err"):  # 跳过失败交易
            continue
        
        # 简化检测：大额度转账可能是新币
        pre_balances = meta.get("preBalances", [])
        post_balances = meta.get("postBalances", [])
        
        # 检查日志中是否有 Token 相关指令
        log_messages = meta.get("logMessages", [])
        for log in log_messages:
            if "initializeMint" in log or "CreateAccount" in log:
                new_tokens.append({
                    "signature": tx["transaction"]["signatures"][0][:20] + "...",
                    "slot": block_data.get("blockHeight"),
                    "timestamp": datetime.fromtimestamp(block_data.get("blockTime", 0)).isoformat()
                })
                break
    
    return new_tokens

def monitor():
    """主监控循环"""
    print(f"{'='*60}")
    print(f"Solana 新币发射监控 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    slot = get_latest_slot()
    if not slot:
        print("❌ 无法连接 Solana RPC")
        return
    
    print(f"当前区块: {slot}")
    
    block = get_block(slot)
    if not block:
        print("❌ 无法获取区块数据")
        return
    
    tokens = detect_new_tokens(block)
    
    if tokens:
        print(f"\n🚨 发现 {len(tokens)} 个新币发射:")
        for t in tokens:
            print(f"  • 交易: {t['signature']}")
            print(f"    时间: {t['timestamp']}")
    else:
        print("\n📭 该区块暂无新币发射")
    
    print(f"\n{'='*60}")

if __name__ == "__main__":
    monitor()
