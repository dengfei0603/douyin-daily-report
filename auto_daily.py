"""???? - 7?7?????"""
import os, sys, json, re, base64
from datetime import datetime, timezone

TOKEN = os.environ.get("GITHUB_TOKEN", "")
OWNER = "dengfei0603"
REPO = "douyin-daily-report"
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "")

HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
API = f"https://api.github.com/repos/{OWNER}/{REPO}"

CATEGORIES = [
    {"day": 0, "name": "??", "label": "????", "icon": "\U0001f3e0"},
    {"day": 1, "name": "??", "label": "????", "icon": "\U0001f4e6"},
    {"day": 2, "name": "??", "label": "????", "icon": "\U0001f373"},
    {"day": 3, "name": "??", "label": "????", "icon": "\U0001f9f4"},
    {"day": 4, "name": "??", "label": "????", "icon": "\U0001f9f9"},
    {"day": 5, "name": "??", "label": "????", "icon": "\u2615"},
    {"day": 6, "name": "??", "label": "????", "icon": "\U0001f6cf\ufe0f"},
]

def load_cache():
    try:
        import requests
        resp = requests.get(f"{API}/contents/cache/products.json", headers=HEADERS)
        if resp.status_code == 200:
            return json.loads(base64.b64decode(resp.json()["content"]).decode("utf-8"))
    except:
        pass
    return {"categories": {}, "timestamp": ""}

def main():
    weekday = datetime.now(timezone.utc).weekday()
    today_cat = CATEGORIES[weekday]
    
    print(f"\U0001f680 \u6296\u97f3\u65e5\u62a5 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 40)
    
    cache = load_cache()
    cat_data = cache.get("categories", {}).get(today_cat["label"], [])
    
    if not cat_data:
        print(f"\u274c {today_cat['label']} \u65e0\u6570\u636e")
        return 1
    
    print(f"\U0001f4e6 {today_cat['icon']} {today_cat['label']}: {len(cat_data)} \u4e2a\u5546\u54c1")
    
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
    print(f"\U0001f3af \u7cbe\u9009 {len(picked)} \u4e2a")
    
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    content = f"\U0001f4ca **\u6296\u97f3\u8fbe\u4eba\u65e5\u62a5**\n\U0001f4c5 {today_str} {today_cat['name']} | {today_cat['icon']} {today_cat['label']}\n\U0001f4cd7\u59297\u54c1\u7c7b\u5faa\u73af\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n"
    
    for i, p in enumerate(picked):
        content += f"**#{i+1} {p.get('name', '')[:50]}**\n"
        content += f"\U0001f4b0 \u4f63\u91d1 {p.get('commission', '-')}  \U0001f4c8 \u6708\u9500 {p.get('monthly_sales', '-')}\n"
        ch = p.get("sales_channel", {})
        content += f"\U0001f4f9 \u77ed\u89c6\u9891 {ch.get('video', '-')}  \U0001f4e1 \u76f4\u64ad {ch.get('live', '-')}  \U0001f6d2 \u5546\u54c1\u5361 {ch.get('card', '-')}\n"
        videos = p.get("video_links", [])
        if videos:
            content += f"\U0001f517 {videos[0].get('url', '')}\n"
        content += "\n"
    
    content += "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\U0001f916 \u6bcf\u65e5\u81ea\u52a8\u63a8\u9001 | 7\u59297\u54c1\u7c7b\u5faa\u73af"
    
    if PUSHPLUS_TOKEN:
        import requests
        resp = requests.post("https://www.pushplus.plus/send", json={
            "token": PUSHPLUS_TOKEN,
            "title": f"\U0001f4ca \u6296\u97f3\u65e5\u62a5 {today_str} {today_cat['name']} {today_cat['label']}",
            "content": content,
            "template": "markdown"
        })
        print(f"PushPlus: {chr(10004) if resp.status_code == 200 else chr(10008)} - {resp.text[:100]}")
    
    print("\u2705 \u5b8c\u6210")

if __name__ == "__main__":
    main()
