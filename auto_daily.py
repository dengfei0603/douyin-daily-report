"""抖音日报 - 日用百货单品版"""
import os, sys, json, re, base64, requests
from datetime import datetime, timezone

TOKEN = os.environ.get("GITHUB_TOKEN", "")
OWNER = "dengfei0603"
REPO = "douyin-daily-report"
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "")

HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
API = f"https://api.github.com/repos/{OWNER}/{REPO}"

def load_cache():
    try:
        resp = requests.get(f"{API}/contents/cache/products.json", headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            return json.loads(base64.b64decode(resp.json()["content"]).decode("utf-8"))
    except:
        pass
    return {"categories": {}, "timestamp": ""}

def main():
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"抖音日报 {today_str} | 日用百货")
    
    cache = load_cache()
    products = cache.get("categories", {}).get("日用百货", [])
    if not products:
        print("无数据")
        return 1
    
    p = products[0]
    sep = "\u2501" * 15
    content = f"**\ud83d\udcc8 抖音达人日报**\n{today_str} | \ud83c\udfe0 日用百货\n单品类每日推送\n{sep}\n\n"
    content += f"**\ud83c\udf1f 今日选品**\n{p.get('name', '')[:50]}\n"
    content += f"\ud83d\udcb0 佣金 {p.get('commission', '-')}\n\n"
    content += f"**\ud83d\udcf9 爆款视频**\n"
    vids = p.get("video_links", [])
    for i, v in enumerate(vids[:5]):
        url = v.get("url", "")
        author = v.get("author", "")
        desc = v.get("desc", "")
        content += f"\n#{i+1} \u2022 作者: {author}\n   \ud83d\udd17 {url}\n"
        if desc:
            content += f"   \ud83d\udcdd {desc[:50]}\n"
    
    content += f"\n{sep}\n\ud83e\udd16 AI提示词\n"
    if vids:
        desc1 = vids[0].get("desc", "")
        name = p.get("name", "")[:20]
        content += f"> 以{name}为例，脚本结构:\n"
        content += f"> 开头(痛点): {desc1[:30]}...\n"
        content += f"> 中间(展示): 产品效果对比\n"
        content += f"> 结尾(引导): 点击左下角小黄车\n"
    
    content += f"\n{sep}\n\ud83d\udce9 每日自动推送"
    
    if PUSHPLUS_TOKEN:
        resp = requests.post("https://www.pushplus.plus/send", json={
            "token": PUSHPLUS_TOKEN,
            "title": f"\ud83d\udcc8 抖音日报 {today_str} 日用百货",
            "content": content,
            "template": "markdown"
        })
        print(f"PushPlus: {resp.status_code}")
        print(content[:300])

if __name__ == "__main__":
    main()
