from datetime import datetime
import feedparser
import pandas as pd
import os

# RSS取得対象
RSS_FEEDS = {
    "Reuters": "http://feeds.reuters.com/reuters/topNews",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "Associated Press": "https://apnews.com/rss",
    "Investopedia": "https://www.investopedia.com/feedbuilder/feed/getfeed/?feedName=rss_headline"
}

# 出力フォルダ
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
                "link": entry.link,
                "published": entry.get("published", ""),
                "summary": entry.get("summary", "")
            })

    df = pd.DataFrame(all_entries)
    df.to_csv(f"{FOLDER}/rss_{DATE_STR}.csv", index=False)
    print(f"✅ Saved {len(df)} items → logs/rss_{DATE_STR}.csv")

collect_rss()
