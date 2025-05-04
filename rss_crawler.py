from datetime import datetime
import os
import pandas as pd
import requests
import feedparser
from bs4 import BeautifulSoup

# 出力先
FOLDER = "logs"
DATE_STR = datetime.utcnow().strftime("%Y-%m-%d_%H%M")
HEADERS = {"User-Agent": "Mozilla/5.0"}

# 各URL
ALJAZEERA_RSS = "https://www.aljazeera.com/xml/rss/all.xml"
AP_URL = "https://apnews.com/apf-topnews"
INVESTOPEDIA_URL = "https://www.investopedia.com/news/"
REUTERS_URL = "https://www.reuters.com/world/"

def collect_rss():
    os.makedirs(FOLDER, exist_ok=True)
    all_entries = []

    # --- Al Jazeera (RSS) ---
    try:
        print(f"[Al Jazeera] fetching {ALJAZEERA_RSS}")
        feed = feedparser.parse(ALJAZEERA_RSS)
        print(f"[Al Jazeera] {len(feed.entries)} entries retrieved")

        for i, entry in enumerate(feed.entries[:20]):
            all_entries.append({
                "site": "Al Jazeera",
                "rank": i + 1,
                "title": entry.title,
                "link": entry.link
            })
    except Exception as e:
        print(f"[Al Jazeera ERROR] {e}")

    # --- AP通信 ---
    try:
        print(f"[AP] fetching {AP_URL}")
        resp = requests.get(AP_URL, headers=HEADERS)
        soup = BeautifulSoup(resp.content, "html.parser")
        links = soup.find_all("a", href=True)

        seen = set()
        count = 0
        for a in links:
            href = a["href"]
            title = a.get_text(strip=True)
            if "/article/" in href and title:
                url = href if href.startswith("http") else f"https://apnews.com{href}"
                if url in seen:
                    continue
                seen.add(url)
                all_entries.append({
                    "site": "Associated Press",
                    "rank": count + 1,
                    "title": title,
                    "link": url
                })
                count += 1
                if count >= 20:
                    break
        print(f"[AP] {count} entries retrieved")
    except Exception as e:
        print(f"[AP ERROR] {e}")

    # --- Investopedia ---
    try:
        print(f"[Investopedia] fetching {INVESTOPEDIA_URL}")
        resp = requests.get(INVESTOPEDIA_URL, headers=HEADERS)
        soup = BeautifulSoup(resp.content, "html.parser")
        links = soup.find_all("a", href=True)

        seen = set()
        count = 0
        for a in links:
            href = a["href"]
            title = a.get_text(strip=True)
            if "/news/" in href and "article" in href and title:
                url = href if href.startswith("http") else f"https://www.investopedia.com{href}"
                if url in seen:
                    continue
                seen.add(url)
                all_entries.append({
                    "site": "Investopedia",
                    "rank": count + 1,
                    "title": title,
                    "link": url
                })
                count += 1
                if count >= 20:
                    break
        print(f"[Investopedia] {count} entries retrieved")
    except Exception as e:
        print(f"[Investopedia ERROR] {e}")

    # --- Reuters ---
    try:
        print(f"[Reuters] fetching {REUTERS_URL}")
        resp = requests.get(REUTERS_URL, headers=HEADERS)
        soup = BeautifulSoup(resp.content, "html.parser")
        links = soup.find_all("a", href=True)

        seen = set()
        count = 0
        for a in links:
            href = a["href"]
            title = a.get_text(strip=True)
            if "/world/" in href and title:
                url = f"https://www.reuters.com{href}" if href.startswith("/") else href
                if url in seen:
                    continue
                seen.add(url)
                all_entries.append({
                    "site": "Reuters",
                    "rank": count + 1,
                    "title": title,
                    "link": url
                })
                count += 1
                if count >= 20:
                    break
        print(f"[Reuters] {count} entries retrieved")
    except Exception as e:
        print(f"[Reuters ERROR] {e}")

    # 保存
    df = pd.DataFrame(all_entries)
    output_path = f"{FOLDER}/rss_{DATE_STR}.csv"
    df.to_csv(output_path, index=False)
    print(f"✅ Saved {len(all_entries)} items ➜ {output_path}")

if __name__ == "__main__":
    collect_rss()



