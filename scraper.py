import feedparser
import hashlib
import json
import os
import requests
import datetime
from openai import OpenAI

# --- 配置区 ---
KEYWORDS = ["AI", "智能体", "Agent", "模型", "架构", "水文", "科学", "OpenClaw", "DeepSeek", "GPT", "Claude", "AI4S", "算法", "Cursor", "编程"]
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

def fetch_and_pool():
    """抓取素材并存入周池子（支持增量存储）"""
    history = json.load(open("history.json", "r")) if os.path.exists("history.json") else []
    if os.path.exists("weekly_pool.json"):
        with open("weekly_pool.json", "r", encoding='utf-8') as f:
            try:
                pool = json.load(f)
            except:
                pool = []
    else:
        pool = []

    sources = [
        {"name": "Arxiv-ML", "url": "https://rss.arxiv.org/rss/cs.LG"},
        {"name": "Arxiv-CV", "url": "https://rss.arxiv.org/rss/cs.CV"},
        {"name": "HF-Daily-Papers", "url": "https://papers.takara.ai/api/feed"},
        {"name": "OpenAI-News", "url": "https://openai.com/news/rss.xml"},
        {"name": "DeepMind-Blog", "url": "https://deepmind.google/blog/feed/basic/"},
        {"name": "HuggingFace-Blog", "url": "https://huggingface.co/blog/feed.xml"},
        {"name": "Meta-AI-Blog", "url": "https://engineering.fb.com/category/ml-applications/feed/"},
        {"name": "Google-AI-Blog", "url": "https://blog.google/technology/ai/rss/"},
        {"name": "Nature-Machine-Intelligence", "url": "http://feeds.nature.com/natmachintell/rss/current"},
        {"name": "MIT-AI-News", "url": "https://news.mit.edu/topic/mitmachine-learning-rss.xml"},
        {"name": "Science-Robotics", "url": "https://www.science.org/journal/scirobotics/rss"},
        {"name": "MarkTechPost", "url": "https://www.marktechpost.com/feed"},
        {"name": "Techmeme-AI", "url": "https://www.techmeme.com/feed.xml"},
        {"name": "Synced-机器之心", "url": "https://www.jiqizhixin.com/rss"},
        {"name": "Reddit-ML", "url": "https://www.reddit.com/r/MachineLearning/.rss"},
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    print(f"开始抓取 RSS 源... 当前池子已有 {len(pool)} 条素材")
    new_count = 0
    for s in sources:
        try:
            resp = requests.get(s['url'], headers=headers, timeout=20)
            feed = feedparser.parse(resp.text)
            for entry in feed.entries:
                item_id = hashlib.md5(entry.link.encode()).hexdigest()
                if item_id not in history:
                    if any(key.lower() in entry.title.lower() for key in KEYWORDS):
                        new_item = {"title": entry.title, "link": entry.link, "source": s['name']}
                        pool.append(new_item)
                        history.append(item_id)
                        new_count += 1
        except Exception as e:
            print(f"抓取 {s['name']} 失败: {e}")
            continue
    
    with open("history.json", "w") as f: 
        json.dump(history[-1000:], f)
    with open("weekly_pool.json", "w", encoding='utf-8') as f: 
        json.dump(pool, f, ensure_ascii=False, indent=2)
    
    print(f"本次新增: {new_count} 条，池子总计: {len(pool)} 条")
    return pool

# 🌟 安全抽样逻辑
def summarize_weekly(pool):
    """召唤 DeepSeek 进行大规模情报汇总（上限 1000 条）"""
    if not pool: return None
    
    import random
    # 如果池子大于 1000，抽 1000 个；否则全选
    sample_size = min(len(pool), 1000)
    selected_items = random.sample(pool, sample_size)
    
    bj_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime('%Y/%m/%d')
    # 构造素材文本
    text_content = "\n".join([f"- {i['title']} (来源: {i['source']})" for i in selected_items])
    
    prompt = f"""
    你现在是《AI水文信息站》总编。今天是 {bj_time}。
    
    【任务】：请从以下提供的 {sample_size} 条真实素材中，提炼出本周全球 AI 与科技界最值得关注的动态。
    【要求】：
    1. 严禁虚构。
    2. 归纳总结，不要流水账。
    3. 重点关注具有技术突破或行业趋势的内容。
    
    素材列表：
    {text_content}
    """
    
    print(f"📡 正在向 DeepSeek 发送 {sample_size} 条真实情报...")
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat", 
            messages=[{"role": "user", "content": prompt}], 
            max_tokens=2500, # 🌟 稍微调高输出上限，给它发挥空间
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ DeepSeek 调用失败，可能是 Token 太多或网络波动: {e}")
        return None
        
def upload_to_notion(content, title):
    """将周报上传至 Notion，包含动态配图"""
    token = os.getenv("NOTION_TOKEN")
    db_id = os.getenv("NOTION_DATABASE_ID")
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    # 🌟 动态封面图
    cover_image_url = "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1000"
    
    payload = {
        "parent": {"database_id": db_id},
        "properties": { "Name": {"title": [{"text": {"content": title}}]} },
        "children": [
            {"object": "block", "type": "image", "image": {"type": "external", "external": {"url": cover_image_url}}},
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": content[:2000]}}]}}
        ]
    }
    res = requests.post(url, headers=headers, json=payload)
    return res.status_code == 200

if __name__ == "__main__":
    current_pool = fetch_and_pool() 
    bj_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    weekday = bj_time.weekday() 
    print(f"当前北京时间: {bj_time.strftime('%Y-%m-%d %H:%M')}, 星期{weekday+1}")

    if weekday == 0: 
        print("🚀 检测到周一发布日，正在生成周报...")
        if len(current_pool) > 0:
            report = summarize_weekly(current_pool)
            success = upload_to_notion(report, f"AI水文周报 | {bj_time.strftime('%Y-%m-%d')}")
            if success:
                with open("weekly_pool.json", "w", encoding='utf-8') as f:
                    json.dump([], f)
                print("🔥 本周素材已清空，开启新循环。")
        else:
            print("⚠️ 池子是空的。")
    else:
        print(f"今天星期{weekday+1}，仅完成存稿。周一自动交稿！")
