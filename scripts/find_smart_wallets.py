#!/usr/bin/env python3
"""
聪明钱包发现系统 v0.1
目标：通过链上数据找到真正赚钱的钱包
"""

import requests
import json
from datetime import datetime, timedelta

RPC_URL = "https://api.mainnet-beta.solana.com"

# 示例：监控一个新币对，找早期买家
TOKEN_ADDRESS = "So11111111111111111111111111111111111111112"  # Wrapped SOL

def get_token_accounts(token_address):
    """获取持有该Token的所有账户"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenLargestAccounts",
        "params": [token_address]
    }
    try:
        r = requests.post(RPC_URL, json=payload, timeout=10)
        return r.json().get("result", {}).get("value", [])
    except Exception as e:
        print(f"Error: {e}")
        return []

def analyze_wallet(wallet_address):
    """分析单个钱包的历史交易"""
    # 简化版：检查余额和近期活动
    payload = {
        "jsonrpc": "2.0", 
        "id": 1,
        "method": "getBalance",
        "params": [wallet_address]
    }
    try:
        r = requests.post(RPC_URL, json=payload, timeout=10)
        balance = r.json().get("result", {}).get("value", 0)
        return {
            "address": wallet_address,
            "balance_sol": balance / 1e9,
            "status": "active" if balance > 0 else "empty"
        }
    except:
        return None

def find_smart_wallets():
    """主函数：找聪明钱包"""
    print("="*60)
    print(f"🔍 聪明钱包扫描 | {datetime.now().strftime('%H:%M')}")
    print("="*60)
    
    print(f"\n目标: {TOKEN_ADDRESS[:20]}...")
    print("策略: 找大额持有者 → 分析交易历史 → 分级\n")
    
    accounts = get_token_accounts(TOKEN_ADDRESS)
    print(f"找到 {len(accounts)} 个持有者")
    
    smart_wallets = []
    
    for i, acc in enumerate(accounts[:10]):  # 只看前10
        amount = int(acc.get("amount", 0)) / 1e9
        address = acc.get("address", "")
        
        print(f"\n{i+1}. {address[:20]}...")
        print(f"   持有: {amount:.2f} SOL")
        
        # 简化的聪明钱包判断
        if amount > 1000:  # 持有超过1000 SOL
            wallet_info = analyze_wallet(address)
            if wallet_info:
                tier = "T1" if amount > 10000 else "T2"
                smart_wallets.append({
                    "address": address,
                    "tier": tier,
                    "amount": amount
                })
                print(f"   🏆 标记为 {tier} 级聪明钱包")
    
    print("\n" + "="*60)
    print(f"📊 发现 {len(smart_wallets)} 个潜在聪明钱包")
    print("="*60)
    
    return smart_wallets

if __name__ == "__main__":
    wallets = find_smart_wallets()
    
    # 保存结果
    with open("/tmp/smart_wallets_found.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "wallets": wallets
        }, f, indent=2)
    
    print(f"\n💾 结果已保存: /tmp/smart_wallets_found.json")
