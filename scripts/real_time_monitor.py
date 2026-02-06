#!/usr/bin/env python3
"""
聪明钱包发现系统 - 真实数据版
"""

import requests
import json
from datetime import datetime

RPC_URL = "https://api.mainnet-beta.solana.com"

def get_recent_blocks(limit=5):
    """获取最近区块"""
    payload = {"jsonrpc": "2.0", "id": 1, "method": "getSlot"}
    r = requests.post(RPC_URL, json=payload, timeout=10)
    current_slot = r.json().get("result", 0)
    return list(range(current_slot - limit, current_slot))

def find_new_tokens_in_block(slot):
    """在区块中找新币发射"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBlock",
        "params": [slot, {"encoding": "json", "maxSupportedTransactionVersion": 0}]
    }
    
    try:
        r = requests.post(RPC_URL, json=payload, timeout=15)
        result = r.json().get("result", {})
        
        if not result:
            return []
        
        new_tokens = []
        txs = result.get("transactions", [])
        
        for tx in txs:
            meta = tx.get("meta", {})
            if meta.get("err"):
                continue
            
            logs = meta.get("logMessages", [])
            for log in logs:
                if any(k in log for k in ["initializeMint", "InitializeMint", "createMint"]):
                    sig = tx["transaction"]["signatures"][0]
                    accounts = tx["transaction"]["message"]["accountKeys"]
                    
                    new_tokens.append({
                        "signature": sig,
                        "slot": slot,
                        "creator": accounts[0] if accounts else "unknown",
                        "all_accounts": accounts[:5]  # 前5个相关账户
                    })
                    break
        
        return new_tokens
    except Exception as e:
        return []

def main():
    print("="*70)
    print(f"🎯 聪明钱包实时监控 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    blocks = get_recent_blocks(limit=5)
    print(f"\n📡 扫描最新 {len(blocks)} 个区块: {blocks[0]} - {blocks[-1]}")
    
    all_new_tokens = []
    for slot in blocks:
        tokens = find_new_tokens_in_block(slot)
        all_new_tokens.extend(tokens)
    
    print(f"\n🚨 发现 {len(all_new_tokens)} 个新币发射")
    
    if not all_new_tokens:
        print("\n⚠️ 暂无新币发射")
        return
    
    print("\n" + "-"*70)
    for i, token in enumerate(all_new_tokens, 1):
        print(f"\n💎 新币 #{i}")
        print(f"   交易签名: {token['signature']}")
        print(f"   区块高度: {token['slot']}")
        print(f"   创建者:   {token['creator']}")
        print(f"   相关账户: {', '.join(token['all_accounts'][:3])}")
        print(f"   Solscan:  https://solscan.io/tx/{token['signature']}")
        
        # 标记创建者为潜在聪明钱包
        print(f"\n   🏆 标记创建者为观察对象")
        print(f"      地址: {token['creator']}")
        print(f"      理由: 该地址发起新币发射，需追踪其历史收益")
    
    print("\n" + "="*70)
    print(f"📊 总计: {len(all_new_tokens)} 个新币, {len(all_new_tokens)} 个创建者待追踪")
    print("="*70)
    
    # 保存到文件
    with open("/tmp/new_tokens_found.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "count": len(all_new_tokens),
            "tokens": all_new_tokens
        }, f, indent=2)
    
    print(f"\n💾 完整数据: /tmp/new_tokens_found.json")

if __name__ == "__main__":
    main()
