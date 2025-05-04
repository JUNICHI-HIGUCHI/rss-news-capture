from datetime import datetime
import feedparser
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup

# 出力フォルダとファイル名（UTC日時で一意に）
FOLDER = "logs"
DATE_STR = datetime.utcnow().strftime("%Y-%m-%d_%H%M")

# 各媒体の取得先
RSS_FEEDS = {
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "Associated Press": "https://feeds.apnews.com/apf-topnews"
}

INVESTOPEDIA_URL = "https://www.investopedia.com/news/"
REUTERS_URL = "https://www.reuters.com/world/"

def collect_rss():
    os.makedirs(FOLDER, exist_ok=True)
    all_entries = []

    # RSS取得（Al Jazeera, AP）
    for site, url in RSS_FEEDS.items():
        print(f"[{site}] fetching {url}")
        try:
            feed = feedparser.parse(url, request_headers={"User-Agent": "Mozilla/5.0"})
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
            print(f"[{site} ERROR] {e}")

    # Investopedia（HTMLスクレイピング）
    try:
        print(f"[Investopedia] fetching {INVESTOPEDIA_URL}")
        response = requests.get(INVESTOPEDIA_URL, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.content, "html.parser")

        articles = soup.select("a[data-analytics-link='article']")[:20]
        print(f"[Investopedia] {len(articles)} entries retrieved")

        for i, a in enumerate(articles):
            title = a.get_text(strip=True)
            link = a["href"]
            full_url = link if link.startswith("http") else f"https://www.investopedia.com{link}"
            all_entries.append({
                "site": "Investopedia",
                "rank": i + 1,
                "title": title,
                "link": full_url
            })
    except Exception as e:
        print(f"[Investopedia ERROR] {e}")

    # Reuters（HTMLスクレイピング）
    try:
        print(f"[Reuters] fetching {REUTERS_URL}")
        response = requests.get(REUTERS_URL, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.content, "html.parser")

        articles = soup.select("a[href^='/world/'] h3")
        seen = set()

        for i, h3 in enumerate(articles):
            a_tag = h3.find_parent("a")
            title = h3.get_text(strip=True)
            href = a_tag.get("href")
            if not href or not title:
                continue
            full_url = f"https://www.reuters.com{href}" if href.startswith("/") else href
            if full_url in seen:
                continue
            seen.add(full_url)
            all_entries.append({
                "site": "Reuters",
                "rank": i + 1,
                "title": title,
                "link": full_url
            })
            if i >= 19:
                break

        print(f"[Reuters] {len(seen)} articles parsed")
    except Exception as e:
        print(f"[Reuters ERROR] {e}")

    # 保存
    df = pd.DataFrame(all_entries)
    output_path = f"{FOLDER}/rss_{DATE_STR}.csv"
    df.to_csv(output_path, index=False)
    print(f"✅ Saved {len(all_entries)} items ➜ {output_path}")

if __name__ == "__main__":
    collect_rss()

