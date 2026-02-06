#!/usr/bin/env python3
"""
Tier S 信源实时监控
只推送可转化为行动的信息
"""

import os
import subprocess
import re
from datetime import datetime

TIER_S_ACCOUNTS = [
    "CryptoHayes",      # 宏观
    "arthur0x",         # VC
    "packyM",           # 分析
    "bcherny",          # 技术
    "DefiIgnas",        # DeFi
]

KEYWORDS_ACTIONABLE = [
    r"(买入|卖出|做多|做空|抄底)",
    r"(漏洞|风险|警告|危险)",
    r"(上线|发布|融资|空投)",
    r"(策略|方法|教程)",
    r"(\d+%|倍数|x)",  # 具体数字
]

def fetch_tier_s():
    """获取Tier S账号最新推文"""
    results = []
    auth_token = os.getenv('AUTH_TOKEN')
    ct0 = os.getenv('CT0')
    
    for account in TIER_S_ACCOUNTS[:2]:  # 先测试2个
        try:
            cmd = f"export AUTH_TOKEN='{auth_token}' && export CT0='{ct0}' && bird user-tweets {account} -n 5"
            output = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            if output.stdout:
                results.append(f"=== @{account} ===\n{output.stdout[:1000]}")
        except Exception as e:
            results.append(f"@{account}: Error - {e}")
    
    return "\n\n".join(results)

def is_actionable(text):
    """判断是否包含可执行信息"""
    for pattern in KEYWORDS_ACTIONABLE:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def generate_alert():
    content = fetch_tier_s()
    
    report = f"""
{'='*60}
Tier S 信源监控 | {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
{'='*60}

{content}

{'='*60}
筛选标准: 可执行信息 (买入/卖出/风险/工具/策略)
{'='*60}
"""
    return report

if __name__ == "__main__":
    print(generate_alert())
