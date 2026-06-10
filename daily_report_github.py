"""抖音日报 - GitHub Actions 专用版本"""
import os
import sys
import json
import requests

# 从环境变量读取token
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(BASE_DIR, "cache", "products.json")
REPORT_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORT_DIR, exist_ok=True)

def load_products():
    """加载商品数据"""
    if not os.path.exists(CACHE_FILE):
        print("No product data found")
        return []
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("products", [])

def pick_top(products, n=3):
    """按佣金+销量评分选Top3"""
    def score(p):
        s = 0
        import re
        com = re.search(r"(\d+)%", str(p.get("commission", "0")))
        if com:
            s += float(com.group(1))
        sales = str(p.get("monthly_sales", ""))
        if "10w+" in sales:
            s += 30
        elif "5w" in sales:
            s += 20
        elif "1w" in sales:
            s += 10
        return s
    products.sort(key=score, reverse=True)
    return products[:n]

def generate_push_content(products):
    """生成推送到微信的内容"""
    from datetime import datetime
    weekdays = ["周一","周二","周三","周四","周五","周六","周日"]
    today = datetime.now().strftime("%Y-%m-%d")
    wd = weekdays[datetime.now().weekday()]
    
    content = f"📊 **抖音达人日报**\n"
    content += f"📅 {today} {wd} | 品类: 日用百货\n"
    content += "━━━━━━━━━━━━━━━\n\n"
    
    for i, p in enumerate(products):
        content += f"**#{i+1} {p.get('name', '')[:50]}**\n"
        content += f"💰 佣金 {p.get('commission', '-')}  "
        content += f"📈 月销 {p.get('monthly_sales', '-')}\n"
        
        ch = p.get("sales_channel", {})
        content += f"📹 短视频 {ch.get('video', '-')}  "
        content += f"📡 直播 {ch.get('live', '-')}  "
        content += f"🛒 商品卡 {ch.get('card', '-')}\n"
        
        videos = p.get("video_links", [])
        if videos:
            content += f"🔗 多看视频: {videos[0].get('url', '')}\n"
        content += "\n"
    
    content += "━━━━━━━━━━━━━━━\n"
    content += "🤖 每日自动推送 | 数据来源: 蝉妈妈\n"
    content += f"🔄 数据由 Codex AI 更新"
    
    return f"📊 抖音日报 {today}", content

def push_to_wechat(title, content):
    """通过PushPlus推送"""
    if not PUSHPLUS_TOKEN:
        print("PushPlus token not configured")
        return False
    
    resp = requests.post("https://www.pushplus.plus/send", json={
        "token": PUSHPLUS_TOKEN,
        "title": title,
        "content": content,
        "template": "markdown"
    })
    ok = resp.status_code == 200
    print(f"PushPlus: {'OK' if ok else 'Failed'} - {resp.text[:100]}")
    return ok

def main():
    print("=" * 40)
    print("🚀 抖音达人日报 (GitHub Actions)")
    print("=" * 40)
    
    products = load_products()
    if not products:
        print("❌ 无商品数据，请先在Codex中更新")
        return 1
    
    print(f"📦 {len(products)} 个商品")
    picked = pick_top(products, 3)
    print(f"🎯 精选 {len(picked)} 个")
    
    title, content = generate_push_content(picked)
    
    if PUSHPLUS_TOKEN:
        push_to_wechat(title, content)
    else:
        print("⚠️ PushPlus token 未配置")
    
    # Save HTML
    html_path = os.path.join(REPORT_DIR, f"日报_{datetime.now().strftime('%Y%m%d')}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(f"<html><body><pre>{content}</pre></body></html>")
    
    print(f"✅ 完成: {html_path}")
    return 0

if __name__ == "__main__":
    from datetime import datetime
    sys.exit(main())
