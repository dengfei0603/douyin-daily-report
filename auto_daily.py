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
    try:
        resp = requests.get(f"{API}/contents/cache/products.json", headers=HEADERS)
        if resp.status_code == 200:
            return json.loads(base64.b64decode(resp.json()["content"]).decode("utf-8"))
    except:
        pass
    return {"categories": {}, "timestamp": ""}

def main():
    weekday = datetime.now(timezone.utc).weekday()
    today_cat = CATEGORIES[weekday]
    print(f" 抖音日报 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 40)
    cache = load_cache()
    cat_data = cache.get("categories", {}).get(today_cat["label"], [])
    if not cat_data:
        print(f" {today_cat['label']} 无数据")
        return 1
    print(f" {today_cat['icon']} {today_cat['label']}: {len(cat_data)} 个商品")

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
    print(f" 精选 {len(picked)} 个")

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
        print(f"PushPlus: {chr(10004) if resp.status_code == 200 else chr(10008)} - {resp.text[:100]}")

    print("完成")

if __name__ == "__main__":
    main()
