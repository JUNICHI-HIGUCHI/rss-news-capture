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
    "Associated Press": "https://apnews.com/apf-topnews?format=RSS",
    "Investopedia": "https://www.investopedia.com/feedbuilder/feed/getfeed/?feedName=rss_news"
}

# ロイターのスクレイピング対象URL（ワールドニュース）
REUTERS_URL = "https://www.reuters.com/world/"

def collect_rss():
    os.makedirs(FOLDER, exist_ok=True)
    all_entries = []

    # RSS経由の取得
    for site, url in RSS_FEEDS.items():
        print(f"[{site}] fetching {url}")
        try:
            feed = feedparser.parse(url, request_headers={'User-Agent': 'Mozilla/5.0'})
            if feed.bozo:
                print(f"[{site} ERROR] feedparser failed: {feed.bozo_exception}")
                continue
            print(f"[{site}] {len(feed.entries)} entries retrieved")

            for i, entry in enumerate(feed.entries):
                all_entries.append({
                    "site": site,
                    "rank": i + 1,
                    "title": entry.title,
                    "link": entry.link
                })
        except Exception as e:
            print(f"[{site} ERROR] Exception occurred: {e}")

    # ロイターのスクレイピング処理
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(REUTERS_URL, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        articles = soup.select("article a[href*='/world/']")
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
            if i >= 19:
                break

        print(f"[Reuters] {len(seen_links)} articles parsed")

    except Exception as e:
        print(f"[Reuters ERROR] {e}")

    # 保存
    df = pd.DataFrame(all_entries)
    output_path = f"{FOLDER}/rss_{DATE_STR}.csv"
    df.to_csv(output_path, index=False)
    print(f"✅ Saved {len(all_entries)} items ➜ {output_path}")

if __name__ == "__main__":
    collect_rss()

