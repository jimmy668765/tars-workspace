#!/usr/bin/env python3
"""
Twitter/X 发帖脚本 - 使用真实浏览器 headers 伪装
"""
import requests
import json
import os
from datetime import datetime

# 从环境变量读取凭证
AUTH_TOKEN = "d59346f39b0750a1f0c15f3ec967974362945df7"
CT0 = "c417b18169c4ee27c1546d825cacbb7a88fef551a66fb19c291a47c3a7ff90eebfab23141d3ebbaa559fc297e9008b6fc47ae81a7f808e19a32cc40f5492c1c826d73e21631e2d02a86956a0a2cd099b"

def post_tweet(text):
    """使用 GraphQL API 发帖"""
    
    # 真实浏览器 headers
    headers = {
        "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
        "x-csrf-token": CT0,
        "x-twitter-auth-type": "OAuth2Session",
        "x-twitter-client-language": "en",
        "content-type": "application/json",
        "origin": "https://x.com",
        "referer": "https://x.com/home",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "cookie": f"auth_token={AUTH_TOKEN}; ct0={CT0}"
    }
    
    # GraphQL endpoint for creating tweet
    url = "https://x.com/i/api/graphql/VfV5vD2GjVLnzw9WQCnj3g/CreateTweet"
    
    payload = {
        "variables": {
            "tweet_text": text,
            "dark_request": False,
            "media": {
                "media_entities": [],
                "possibly_sensitive": False
            },
            "semantic_annotation_ids": []
        },
        "features": {
            "tweetypie_unmention_optimization_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "responsive_web_twitter_article_tweet_consumption_enabled": False,
            "tweet_awards_web_tipping_enabled": False,
            "responsive_web_home_pinned_timelines_enabled": True,
            "longform_notetweets_rich_text_read_enabled": True,
            "longform_notetweets_inline_media_enabled": True,
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "responsive_web_media_download_video_enabled": False,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "responsive_web_enhance_cards_enabled": False
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            tweet_id = data.get("data", {}).get("create_tweet", {}).get("tweet_results", {}).get("result", {}).get("rest_id")
            if tweet_id:
                print(f"✅ 发帖成功！Tweet ID: {tweet_id}")
                return True
        
        return False
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

if __name__ == "__main__":
    tweet_text = f"TARS online 🤖 Testing automation. Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
    print(f"发送推文: {tweet_text}")
    post_tweet(tweet_text)
