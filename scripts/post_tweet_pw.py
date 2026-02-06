#!/usr/bin/env python3
"""
Twitter/X 发帖 - Playwright 浏览器模拟
"""
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime

AUTH_TOKEN = "d59346f39b0750a1f0c15f3ec967974362945df7"
CT0 = "c417b18169c4ee27c1546d825cacbb7a88fef551a66fb19c291a47c3a7ff90eebfab23141d3ebbaa559fc297e9008b6fc47ae81a7f808e19a32cc40f5492c1c826d73e21631e2d02a86956a0a2cd099b"

TWEET_TEXT = f"TARS online 🤖 Testing browser automation. Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"

async def post_tweet():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
        )
        
        # 注入 cookies
        await context.add_cookies([
            {"name": "auth_token", "value": AUTH_TOKEN, "domain": ".x.com", "path": "/"},
            {"name": "ct0", "value": CT0, "domain": ".x.com", "path": "/"},
        ])
        
        page = await context.new_page()
        
        try:
            print("🌐 打开 X.com...")
            await page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)
            
            # 截图看状态
            await page.screenshot(path="/tmp/twitter_start.png")
            print("📸 已截图 /tmp/twitter_start.png")
            
            # 找发帖框 - 通常是 aria-label="Post text" 或 placeholder="What is happening?!"
            print("📝 寻找发帖框...")
            
            # 尝试多种选择器
            selectors = [
                '[data-testid="tweetTextarea_0"]',
                'div[contenteditable="true"][aria-label*="post" i]',
                'div[contenteditable="true"][aria-label*="Post" i]',
                'div[contenteditable="true"][aria-label*="what" i]',
                'div[contenteditable="true"]',
            ]
            
            tweet_box = None
            for sel in selectors:
                try:
                    tweet_box = await page.wait_for_selector(sel, timeout=5000)
                    if tweet_box:
                        print(f"✅ 找到发帖框: {sel}")
                        break
                except:
                    continue
            
            if not tweet_box:
                print("❌ 没找到发帖框，可能需要先登录或刷新 cookies")
                # 检查页面状态
                content = await page.content()
                if "login" in content.lower() or "sign in" in content.lower():
                    print("⚠️ 需要重新登录，cookies 可能过期了")
                return False
            
            # 点击并输入
            await tweet_box.click()
            await asyncio.sleep(0.5)
            await tweet_box.fill(TWEET_TEXT)
            print(f"✍️ 输入内容: {TWEET_TEXT}")
            
            # 找 Post 按钮
            post_button = await page.wait_for_selector('[data-testid="tweetButtonInline"]', timeout=5000)
            if not post_button:
                post_button = await page.wait_for_selector('button:has-text("Post")', timeout=5000)
            
            if post_button:
                await post_button.click()
                print("🚀 点击 Post 按钮！")
                await asyncio.sleep(3)
                
                # 截图确认
                await page.screenshot(path="/tmp/twitter_posted.png")
                print("📸 已截图 /tmp/twitter_posted.png")
                
                # 检查成功
                current_url = page.url
                if "compose" in current_url or "status" in current_url:
                    print(f"✅ 发帖成功！URL: {current_url}")
                    return True
                else:
                    print(f"⚠️ 不确定是否成功，当前 URL: {current_url}")
                    return True  # 假设成功
            else:
                print("❌ 没找到 Post 按钮")
                return False
                
        except Exception as e:
            print(f"❌ 错误: {e}")
            await page.screenshot(path="/tmp/twitter_error.png")
            print("📸 错误截图: /tmp/twitter_error.png")
            return False
        finally:
            await browser.close()

if __name__ == "__main__":
    result = asyncio.run(post_tweet())
    exit(0 if result else 1)
