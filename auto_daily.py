"""抖音日报 - 自动采集+生成一体脚本（GitHub Actions版）"""
import os, sys, json, re, io, zipfile, base64
from datetime import datetime

# ===== 配置 =====
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OWNER = "dengfei0603"
REPO = "douyin-daily-report"
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "")

HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
API = f"https://api.github.com/repos/{OWNER}/{REPO}"

def load_cache():
    """从GitHub加载当前products.json"""
    try:
        import requests
        resp = requests.get(f"{API}/contents/cache/products.json", headers=HEADERS)
        if resp.status_code == 200:
            content = base64.b64decode(resp.json()["content"]).decode("utf-8")
            return json.loads(content)
    except:
        pass
    return {"products": [], "timestamp": ""}

def save_cache(data):
    """保存products.json到GitHub"""
    try:
        import requests
        # Get current file sha
        resp = requests.get(f"{API}/contents/cache/products.json", headers=HEADERS)
        sha = resp.json().get("sha", "") if resp.status_code == 200 else ""
        
        content = base64.b64encode(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")).decode("utf-8")
        body = {
            "message": f"自动更新数据 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "content": content,
            "sha": sha,
            "branch": "main"
        }
        resp = requests.put(f"{API}/contents/cache/products.json", headers=HEADERS, json=body)
        return resp.status_code in [200, 201]
    except:
        return False

def try_scrape():
    """尝试从蝉妈妈抓取最新数据（多种方法）"""
    
    # 方法1: 尝试API endpoint
    api_urls = [
        "https://www.chanmama.com/api/promotionRank/tikGoodsSale",
        "https://www.chanmama.com/promotionRank/tikGoodsSale/data",
        "https://api.chanmama.com/promotion/rank/goods",
    ]
    
    import requests
    for url in api_urls:
        try:
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.chanmama.com/"}, timeout=10)
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    if data and "data" in data:
                        print(f"✅ API抓取成功: {url}")
                        return data["data"]
                except:
                    pass
        except:
            pass
    
    # 方法2: 尝试解析页面文本
    try:
        # 使用Playwright (如果可用)
        pass  # GitHub runner上太慢，跳过
    except:
        pass
    
    return None

def main():
    print(f"🚀 抖音日报 全自动版 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 40)
    
    # 尝试抓取新数据
    print("📡 尝试抓取蝉妈妈数据...")
    new_data = try_scrape()
    
    # 加载现有缓存
    cache = load_cache()
    
    if new_data:
        print("✅ 抓到新数据!")
        cache["products"] = new_data if isinstance(new_data, list) else new_data.get("list", cache["products"])
        cache["timestamp"] = datetime.now().isoformat()
        save_cache(cache)
    else:
        print("⚠️ 抓取失败，使用缓存数据")
    
    products = cache.get("products", [])
    if not products:
        print("❌ 无数据")
        return 1
    
    print(f"📦 {len(products)} 个商品")
    
    # 挑选Top 3
    def score(p):
        s = 0
        com = re.search(r"(\d+)%", str(p.get("commission", "")))
        if com: s += float(com.group(1))
        sales = str(p.get("monthly_sales", ""))
        if "10w+" in sales: s += 30
        elif "5w" in sales: s += 20
        return s
    
    products.sort(key=score, reverse=True)
    picked = products[:3]
    print(f"🎯 精选 {len(picked)} 个")
    
    # 生成推送内容
    weekdays = ["周一","周二","周三","周四","周五","周六","周日"]
    today = datetime.now().strftime("%Y-%m-%d")
    wd = weekdays[datetime.now().weekday()]
    
    content = f"📊 **抖音达人日报**\n📅 {today} {wd} | 品类: 日用百货\n━━━━━━━━━━━━━━━\n\n"
    
    for i, p in enumerate(picked):
        content += f"**#{i+1} {p.get('name', '')[:50]}**\n"
        content += f"💰 佣金 {p.get('commission', '-')}  📈 月销 {p.get('monthly_sales', '-')}\n"
        ch = p.get("sales_channel", {})
        content += f"📹 短视频 {ch.get('video', '-')}  📡 直播 {ch.get('live', '-')}  🛒 商品卡 {ch.get('card', '-')}\n"
        videos = p.get("video_links", [])
        if videos:
            content += f"🔗 {videos[0].get('url', '')}\n"
        content += "\n"
    
    content += "━━━━━━━━━━━━━━━\n🤖 每日自动推送"
    
    # 推送微信
    if PUSHPLUS_TOKEN:
        import requests
        resp = requests.post("https://www.pushplus.plus/send", json={
            "token": PUSHPLUS_TOKEN,
            "title": f"📊 抖音日报 {today}",
            "content": content,
            "template": "markdown"
        })
        print(f"PushPlus: {'✅ OK' if resp.status_code == 200 else '❌ Failed'} - {resp.text[:100]}")
    
    print("✅ 完成")

if __name__ == "__main__":
    main()
