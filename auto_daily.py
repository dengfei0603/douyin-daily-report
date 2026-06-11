"""抖音日报 - 7天7品类循环版"""
import os, sys, json, re, base64
from datetime import datetime, timezone

TOKEN = os.environ.get("GITHUB_TOKEN", "")
OWNER = "dengfei0603"
REPO = "douyin-daily-report"
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "")

HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
API = f"https://api.github.com/repos/{OWNER}/{REPO}"

CATEGORIES = [
    {"day": 0, "name": "周一", "label": "日用百货", "icon": "🏠"},
    {"day": 1, "name": "周二", "label": "收纳整理", "icon": "📦"},
    {"day": 2, "name": "周三", "label": "厨房好物", "icon": "🍳"},
    {"day": 3, "name": "周四", "label": "个护清洁", "icon": "🧴"},
    {"day": 4, "name": "周五", "label": "家居清洁", "icon": "🧹"},
    {"day": 5, "name": "周六", "label": "食品冲调", "icon": "☕"},
    {"day": 6, "name": "周日", "label": "家纺布艺", "icon": "🛏️"},
]

def load_cache():
    import requests
    try:
        resp = requests.get(f"{API}/contents/cache/products.json", headers=HEADERS, timeout=15)
        print(f"Cache HTTP: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            raw = base64.b64decode(data["content"])
            text = raw.decode("utf-8")
            obj = json.loads(text)
            cats = obj.get("categories", {})
            print(f"Categories found: {list(cats.keys())}")
            return obj
    except Exception as e:
        print(f"Cache error: {e}")
    return {"categories": {}, "timestamp": ""}

def main():
    weekday = datetime.now(timezone.utc).weekday()
    today_cat = CATEGORIES[weekday]
    print(f"Today: weekday={weekday}, label={today_cat['label']}")

    cache = load_cache()
    cat_data = cache.get("categories", {}).get(today_cat["label"], [])
    print(f"cat_data len: {len(cat_data)}")

    if not cat_data:
        print("No data, will exit")
        return 1

    def score(p):
        s = 0
        com = re.search(r"(\d+)%", str(p.get("commission", "")))
        if com: s += float(com.group(1))
        sales = str(p.get("monthly_sales", ""))
        if "10w+" in sales: s += 30
        elif "5w" in sales: s += 20
        elif "1w" in sales: s += 10
        ch = p.get("sales_channel", {})
        v = str(ch.get("video", "0")).replace("%","")
        try: s += float(v) * 0.3
        except: pass
        return s

    cat_data.sort(key=score, reverse=True)
    picked = cat_data[:3]
    print(f"Picked: {len(picked)}")

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    content = f"**抖音达人日报**\n{today_str} {today_cat['name']} | {today_cat['icon']} {today_cat['label']}\n7天7品类循环\n" + "━" * 15 + "\n\n"

    for i, p in enumerate(picked):
        content += f"**#{i+1} {p.get('name', '')[:50]}**\n"
        content += f"佣金 {p.get('commission', '-')}  月销 {p.get('monthly_sales', '-')}\n"
        ch = p.get("sales_channel", {})
        content += f"短视频 {ch.get('video', '-')}  直播 {ch.get('live', '-')}  商品卡 {ch.get('card', '-')}\n"
        videos = p.get("video_links", [])
        if videos:
            content += f"{videos[0].get('url', '')}\n"
        content += "\n"

    content += "━" * 15 + "\n每日自动推送 | 7天7品类循环"

    if PUSHPLUS_TOKEN:
        resp = requests.post("https://www.pushplus.plus/send", json={
            "token": PUSHPLUS_TOKEN,
            "title": f"抖音日报 {today_str} {today_cat['name']} {today_cat['label']}",
            "content": content,
            "template": "markdown"
        })
        print(f"PushPlus: {resp.status_code} {resp.text[:80]}")

if __name__ == "__main__":
    main()
