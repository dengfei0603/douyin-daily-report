"""抖音日报 - 7天7品类循环版（含视频链接+脚本）"""
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

HOOKS = {
    "\u65e5\u7528\u767e\u8d27": "\u4f60\u5bb6\u662f\u4e0d\u662f\u4e5f\u6709\u8fd9\u4e9b\u6e05\u6d01\u96be\u9898\uff1f",
    "\u98df\u54c1\u996e\u6599": "\u8fd9\u4e2a\u5473\u9053\u771f\u7684\u7edd\u4e86\uff01",
    "\u5bb6\u5c45\u5bb6\u7eba": "\u6362\u4e0a\u4e4b\u540e\u6863\u6b21\u77ac\u95f4\u63d0\u5347\uff01",
    "\u53a8\u536b\u5bb6\u7535": "\u53a8\u623f\u5c0f\u767d\u4e5f\u80fd\u8f7b\u677e\u641e\u5b9a\uff01",
    "\u7f8e\u5986\u62a4\u80a4": "\u56de\u8d2d\u4e8610\u6b21\u7684\u5b9d\u85cf\uff01",
    "\u8fd0\u52a8\u6237\u5916": "\u4e0d\u7528\u53bb\u5065\u8eab\u623f\uff01",
    "\u6bcd\u5a74\u7528\u54c1": "\u5f53\u5988\u4e4b\u540e\u624d\u77e5\u9053\u7684\u597d\u4e1c\u897f\uff01"
}

def load_cache():
    try:
        resp = requests.get(f"{API}/contents/cache/products.json", headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            return json.loads(base64.b64decode(resp.json()["content"]).decode("utf-8"))
    except:
        pass
    return {"categories": {}, "timestamp": ""}

def make_script(name, label):
    hook = HOOKS.get(label, "\u8fd9\u6b3e\u4ea7\u54c1\u592a\u597d\u7528\u4e86\uff01")
    n = name[:15]
    return f"\u3010\u5f00\u59343\u79d2\u3011{hook}\n\u30105-10\u79d2\u3011\u4eca\u5929\u5b89\u5229{n}\n\u301010-20\u79d2\u3011\u54c1\u8d28\u597d/\u4ef7\u683c\u5b9e\u60e0/\u6296\u97f3\u7206\u6b3e\n\u301020-25\u79d2\u3011\u70b9\u51fb\u5de6\u4e0b\u89d2\u5c0f\u9ec4\u8f66\u5b89\u6392\u4e0a\uff01"

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
        vc = str(p.get("videoCount", "0"))
        try: s += int(vc) * 0.1
        except: pass
        return s

    cat_data.sort(key=score, reverse=True)
    picked = cat_data[:3]
    print(f"\U0001f3af \u7cbe\u9009 {len(picked)} \u4e2a")

    # Ensure all picked have scripts
    for p in picked:
        vids = p.get("video_links", [])
        if not vids:
            p["video_links"] = [{"url": "", "script": make_script(p.get("name", ""), today_cat["label"])}]

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sep = "\u2501" * 15
    content = f"**\u6296\u97f3\u8fbe\u4eba\u65e5\u62a5**\n{today_str} {today_cat['name']} | {today_cat['icon']} {today_cat['label']}\n7\u59297\u54c1\u7c7b\u5faa\u73af\n{sep}\n\n"

    for i, p in enumerate(picked):
        content += f"**#{i+1} {p.get('name', '')[:50]}**\n"
        content += f"\U0001f4b0 \u4f63\u91d1 {p.get('commission', '-')}  \U0001f4f9 \u89c6\u9891\u6570 {p.get('videoCount', '-')}\n"
        vids = p.get("video_links", [])
        if vids:
            url = vids[0].get("url", "")
            if url:
                content += f"\U0001f517 {url}\n"
            script = vids[0].get("script", "")
            if script:
                for line in script.split("\n")[:4]:
                    if line.strip():
                        content += f"> {line.strip()}\n"
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
