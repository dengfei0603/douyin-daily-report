"""抖音日报 - 7天7品类循环版"""
import os, sys, json, re, base64, requests
from datetime import datetime, timezone

TOKEN = os.environ.get("GITHUB_TOKEN", "")
OWNER = "dengfei0603"
REPO = "douyin-daily-report"
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "")

HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
API = f"https://api.github.com/repos/{OWNER}/{REPO}"

CATEGORIES = [{"day": 0, "name": "周一", "label": "日用百货", "icon": "🏠"}, {"day": 1, "name": "周二", "label": "食品饮料", "icon": "☕"}, {"day": 2, "name": "周三", "label": "家居家纺", "icon": "🛏️"}, {"day": 3, "name": "周四", "label": "厨卫家电", "icon": "🍳"}, {"day": 4, "name": "周五", "label": "美妆护肤", "icon": "🧴"}, {"day": 5, "name": "周六", "label": "运动户外", "icon": "🏃"}, {"day": 6, "name": "周日", "label": "母婴用品", "icon": "👶"}]

HOOKS = {"日用百货": "你家是不是也有这些清洁难题？", "食品饮料": "这个味道真的绝了！", "家居家纺": "换上之后档次瞬间提升！", "厨卫家电": "厨房小白也能轻松搞定！", "美妆护肤": "回购了10次的宝藏！", "运动户外": "不用去健身房！", "母婴用品": "后悔没早买的好东西！"}

def load_cache():
    try:
        resp = requests.get(f"{API}/contents/cache/products.json", headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            return json.loads(base64.b64decode(resp.json()["content"]).decode("utf-8"))
    except Exception as e:
        print(f"Cache load error: {e}")
    return {"categories": {}, "timestamp": ""}

def make_script(name, label):
    hook = HOOKS.get(label, "这款产品太好用了！")
    n = name[:15]
    return f"【开头3秒】{hook}
【5-10秒】今天安利{n}
【10-20秒】品质好/价格实惠/抖音爆款
【20-25秒】点击左下角小黄车安排上！"

def main():
    weekday = datetime.now(timezone.utc).weekday()
    today_cat = CATEGORIES[weekday]
    print(f"抖音日报 {datetime.now().strftime('%Y-%m-%d %H:%M')} | {today_cat['name']} {today_cat['label']}")
    print("=" * 40)

    cache = load_cache()
    cat_data = cache.get("categories", {}).get(today_cat["label"], [])
    if not cat_data:
        print(f"无数据: {today_cat['label']}")
        return 1

    print(f"{today_cat['icon']} {today_cat['label']}: {len(cat_data)} 个商品")

    def score(p):
        s = 0
        com = str(p.get("commission", ""))
        m = re.search(r"(\d+)%", com)
        if m: s += float(m.group(1))
        vc = str(p.get("videoCount", "0"))
        try: s += int(vc) * 0.1
        except: pass
        return s

    cat_data.sort(key=score, reverse=True)
    picked = cat_data[:3]
    print(f"精选 {len(picked)} 个")

    # Ensure scripts for all
    for p in picked:
        vids = p.get("video_links", [])
        if not vids or not vids[0].get("script"):
            p["video_links"] = [{"url": "", "script": make_script(p.get("name", ""), today_cat["label"])}]

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sep = "━" * 15
    content = f"**抖音达人日报**\n{today_str} {today_cat['name']} | {today_cat['icon']} {today_cat['label']}\n7天7品类循环\n{sep}\n\n"

    for i, p in enumerate(picked):
        content += f"**#{i+1} {p.get('name', '')[:50]}**\n"
        content += f"佣金 {p.get('commission', '-')}  |  视频数 {p.get('videoCount', '-')}\n"
        vids = p.get("video_links", [])
        if vids:
            url = vids[0].get("url", "")
            if url:
                content += f"🔗 {url}\n"
            script_txt = vids[0].get("script", "")
            if script_txt:
                for line in script_txt.split("\n")[:4]:
                    if line.strip():
                        content += f"> {line.strip()}\n"
        content += "\n"

    content += f"{sep}\n每日自动推送 | 7天7品类循环"

    if PUSHPLUS_TOKEN:
        resp = requests.post("https://www.pushplus.plus/send", json={
            "token": PUSHPLUS_TOKEN,
            "title": f"抖音日报 {today_str} {today_cat['name']} {today_cat['label']}",
            "content": content,
            "template": "markdown"
        })
        print(f"PushPlus: {resp.status_code} {'OK' if resp.status_code == 200 else 'FAIL'}")
    else:
        print("No token")

if __name__ == "__main__":
    main()
