"""抖音日报 - 7天7品类循环版 v2（修复视频链接+真实脚本）"""
import os, sys, json, re, base64, requests
from datetime import datetime, timezone

TOKEN = os.environ.get("GITHUB_TOKEN", "")
OWNER = "dengfei0603"
REPO = "douyin-daily-report"
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "")

HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
API = f"https://api.github.com/repos/{OWNER}/{REPO}"

CATEGORIES = [
    {"day": 0, "name": "周一", "label": "日用百货", "icon": "🏠"},
    {"day": 1, "name": "周二", "label": "食品饮料", "icon": "☕"},
    {"day": 2, "name": "周三", "label": "家居家纺", "icon": "🛏"},
    {"day": 3, "name": "周四", "label": "厨卫家电", "icon": "🍳"},
    {"day": 4, "name": "周五", "label": "美妆护肤", "icon": "🧴"},
    {"day": 5, "name": "周六", "label": "运动户外", "icon": "🏃"},
    {"day": 6, "name": "周日", "label": "母婴用品", "icon": "👶"}
]

def make_script_from_video(name, desc):
    """Generate script from real video description"""
    n = name[:20]
    d = desc[:50] if desc else "这款产品太好用了"
    return (
        f"【开头3秒】{d}，看完你也会心动！\n"
        f"【5-10秒】今天给大家安利{n}\n"
        f"【10-15秒】这个真的是抖音爆款，好多人都在用\n"
        f"【15-25秒】品质好价格实惠，买到就是赚到\n"
        f"【25-30秒】点击左下角小黄车，赶紧安排上！"
    )

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
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"抖音日报 {today_str} | {today_cat['name']} {today_cat['label']}")

    cache = load_cache()
    cat_data = cache.get("categories", {}).get(today_cat["label"], [])
    if not cat_data:
        print(f"无数据: {today_cat['label']}")
        return 1

    print(f"{today_cat['icon']} {today_cat['label']}: {len(cat_data)} 个商品")

    # Score and pick top 3
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

    sep = "━" * 15
    content = f"**抖音达人日报**\n{today_str} {today_cat['name']} | {today_cat['icon']} {today_cat['label']}\n7天7品类循环\n{sep}\n\n"

    for i, p in enumerate(picked):
        content += f"**#{i+1} {p.get('name', '')[:50]}**\n"
        content += f"佣金 {p.get('commission', '-')} | 视频数 {p.get('videoCount', '-')}\n"
        
        vids = p.get("video_links", [])
        if vids:
            for j, v in enumerate(vids[:3]):
                url = v.get("url", "")
                if url:
                    content += f"🔗 视频{j+1}: {url}\n"
                desc = v.get("desc", "")
                if desc:
                    # Generate script from real description
                    script = make_script_from_video(p.get("name", ""), desc)
                    content += f"📝 脚本:\n"
                    for line in script.split("\n"):
                        if line.strip():
                            content += f"> {line.strip()}\n"
                    break  # Only use first video"s desc for script
        else:
            # Fallback script
            n = p.get("name", "")[:15]
            content += f"📝 脚本:\n> 【开头】今天给大家种草一款好物\n> 【5-15秒】{n}，真的超好用\n> 【15-25秒】品质好价格实惠，赶紧下单\n> 【25-30秒】点击左下角小黄车安排上\n"
        
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
        print(content[:200])
    else:
        print("No PushPlus token")

if __name__ == "__main__":
    main()
