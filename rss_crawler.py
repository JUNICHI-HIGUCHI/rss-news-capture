from datetime import datetime
import feedparser
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup

# RSS取得対象（Al Jazeera / AP / Investopedia）
RSS_FEEDS = {
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "Associated Press": "https://apnews.com/rss",
    "Investopedia": "https://www.investopedia.com/feedbuilder/feed/getfeed/?feedName=rss_headline"
}

# ロイターのトップニュースURL（HTMLスクレイピング用）
REUTERS_URL = "https://www.reuters.com/news/archive/topNews"

# 出力フォルダと日付
FOLDER = "logs"
DATE_STR = datetime.utcnow().strftime("%Y-%m-%d")

def collect_rss():
    os.makedirs(FOLDER, exist_ok=True)
    all_entries = []

    for site, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for i, entry in enumerate(feed.entries):
            all_entries.append({
                "site": site,
                "rank": i + 1,
                "title": entry.title,
                "link": entry.link
            })

    # ロイターのスクレイピング
    try:
        response = requests.get(REUTERS_URL, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.content, "html.parser")
        articles = soup.select("article.story")[:20]  # 最大20件まで

        for i, article in enumerate(articles):
            headline_tag = article.select_one("h3.story-title, h3")
            link_tag = article.select_one("a")
            title = headline_tag.text.strip() if headline_tag else "No Title"
            href = "https://www.reuters.com" + link_tag['href'] if link_tag and link_tag.has_attr("href") else "No Link"

            all_entries.append({
                "site": "Reuters",
                "rank": i + 1,
                "title": title,
                "link": href
            })

    except Exception as e:
        print("Error scraping Reuters:", e)

    # 保存
    df = pd.DataFrame(all_entries)
    output_path = os.path.join(FOLDER, f"rss_{DATE_STR}.csv")
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} items ➜ {output_path}")

if __name__ == "__main__":
    collect_rss()

    df.to_csv(f"{FOLDER}/rss_{DATE_STR}.csv", index=False)
    print(f"✅ Saved {len(df)} items → logs/rss_{DATE_STR}.csv")

collect_rss()
