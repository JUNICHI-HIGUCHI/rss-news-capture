from datetime import datetime
import feedparser
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup

# 出力フォルダと日付
FOLDER = "logs"
DATE_STR = datetime.utcnow().strftime("%Y-%m-%d")

# RSS取得対象（ロイター除く）
RSS_FEEDS = {
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "Associated Press": "https://apnews.com/rss",
    "Investopedia": "https://www.investopedia.com/feedbuilder/feed/getfeed/?feedName=rss_headline"
}

# ロイターのスクレイピング対象URL（ワールドニュース）
REUTERS_URL = "https://www.reuters.com/world/"

def collect_rss():
    os.makedirs(FOLDER, exist_ok=True)
    all_entries = []

    # RSS経由の取得
    for site, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for i, entry in enumerate(feed.entries):
            all_entries.append({
                "site": site,
                "rank": i + 1,
                "title": entry.title,
                "link": entry.link
            })

    # ロイターのスクレイピング処理
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(REUTERS_URL, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        articles = soup.select("article a[href*='/world/']")  # リンクに /world/ を含むものを抽出
        seen_links = set()

        for i, a_tag in enumerate(articles):
            href = a_tag.get("href")
            title = a_tag.get_text(strip=True)
            if not href or not title:
                continue
            full_url = f"https://www.reuters.com{href}" if href.startswith("/") else href
            if full_url in seen_links:
                continue
            seen_links.add(full_url)
            all_entries.append({
                "site": "Reuters",
                "rank": i + 1,
                "title": title,
                "link": full_url
            })
            if i >= 19:  # 上位20件程度で打ち切る（調整可）
                break
    except Exception as e:
        print(f"[Reuters Error] {e}")

    # 保存
    df = pd.DataFrame(all_entries)
    df.to_csv(f"{FOLDER}/rss_{DATE_STR}.csv", index=False)
    print(f"✅ Saved {len(all_entries)} items ➜ logs/rss_{DATE_STR}.csv")

if __name__ == "__main__":
    collect_rss()

