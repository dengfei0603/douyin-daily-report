"""抖音日报 - 7天7品类循环版"""
import os, sys, json, re, base64, requests
from datetime import datetime, timezone

TOKEN = os.environ.get("GITHUB_TOKEN", "")
OWNER = "dengfei0603"
REPO = "douyin-daily-report"
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "")

HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
API = f"https://api.github.com/repos/{OWNER}/{REPO}"

CATEGORIES = [
    {"day": 0, "name": "\u5468\u4e00", "label": "\u65e5\u7528\u767e\u8d27", "icon": "\U0001f3e0"},
    {"day": 1, "name": "\u5468\u4e8c", "label": "\u98df\u54c1\u996e\u6599", "icon": "\u2615"},
    {"day": 2, "name": "\u5468\u4e09", "label": "\u5bb6\u5c45\u5bb6\u7eba", "icon": "\U0001f6cf\ufe0f"},
    {"day": 3, "name": "\u5468\u56db", "label": "\u53a8\u536b\u5bb6\u7535", "icon": "\U0001f373"},
    {"day": 4, "name": "\u5468\u4e94", "label": "\u7f8e\u5986\u62a4\u80a4", "icon": "\U0001f9f4"},
    {"day": 5, "name": "\u5468\u516d", "label": "\u8fd0\u52a8\u6237\u5916", "icon": "\U0001f3c3"},
    {"day": 6, "name": "\u5468\u65e5", "label": "\u6bcd\u5a74\u7528\u54c1", "icon": "\U0001f476"},
]

def load_cache():
    try:
        resp = requests.get(f"{API}/contents/cache/products.json", headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            return json.loads(base64.b64decode(resp.json()["content"]).decode("utf-8"))
    except:
        pass
    return {"categories": {}, "timestamp": ""}

def main():
    weekday = datetime.now(timezone.utc).weekday()
    today_cat = CATEGORIES[weekday]
    print(f"\U0001f680 \u6296\u97f3\u65e5\u62a5 {datetime.now().strftime('%Y-%m-%d %H:%M')} | {today_cat['name']} {today_cat['label']}")
    print("=" * 40)

    cache = load_cache()
    cat_data = cache.get("categories", {}).get(today_cat["label"], [])
    if not cat_data:
        print(f"\u274c {today_cat['label']} \u65e0\u6570\u636e")
        return 1

    print(f"\U0001f4e6 {today_cat['icon']} {today_cat['label']}: {len(cat_data)} \u4e2a\u5546\u54c1")

    def score(p):
        s = 0
        com_text = str(p.get("commission", ""))
        m = re.search(r"(\d+)%", com_text)
        if m: s += float(m.group(1))
        sales = str(p.get("monthly_sales", ""))
        if "10w+" in sales: s += 30
        elif "5w" in sales or "5~10" in sales: s += 20
        elif "2.5" in sales: s += 12
        elif "1w" in sales: s += 8
        return s

    cat_data.sort(key=score, reverse=True)
    picked = cat_data[:3]
    print(f"\U0001f3af \u7cbe\u9009 {len(picked)} \u4e2a")

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sep = "\u2501" * 15
    content = f"**\u6296\u97f3\u8fbe\u4eba\u65e5\u62a5**\n{today_str} {today_cat['name']} | {today_cat['icon']} {today_cat['label']}\n7\u59297\u54c1\u7c7b\u5faa\u73af\n{sep}\n\n"

    for i, p in enumerate(picked):
        content += f"**#{i+1} {p.get('name', '')[:50]}**\n"
        content += f"\U0001f4b0 \u4f63\u91d1 {p.get('commission', '-')}  \U0001f4c8 \u6708\u9500 {p.get('monthly_sales', '-')}\n"
        ch = p.get("sales_channel", {})
        content += f"\U0001f4f9 \u77ed\u89c6\u9891 {ch.get('video', '-')}  \U0001f4e1 \u76f4\u64ad {ch.get('live', '-')}  \U0001f6d2 \u5546\u54c1\u5361 {ch.get('card', '-')}\n"
        videos = p.get("video_links", [])
        if videos and videos[0].get("url"):
            content += f"\U0001f517 {videos[0]['url']}\n"
        content += "\n"

    content += f"{sep}\n\U0001f916 \u6bcf\u65e5\u81ea\u52a8\u63a8\u9001 | 7\u59297\u54c1\u7c7b\u5faa\u73af"

    if PUSHPLUS_TOKEN:
        resp = requests.post("https://www.pushplus.plus/send", json={
            "token": PUSHPLUS_TOKEN,
            "title": f"\U0001f4ca \u6296\u97f3\u65e5\u62a5 {today_str} {today_cat['name']} {today_cat['label']}",
            "content": content,
            "template": "markdown"
        })
        print(f"PushPlus: {resp.status_code} {'OK' if resp.status_code == 200 else 'FAIL'}")
    else:
        print("No PUSHPLUS_TOKEN")

if __name__ == "__main__":
    main()
