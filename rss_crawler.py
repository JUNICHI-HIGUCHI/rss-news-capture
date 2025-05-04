from datetime import datetime
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 出力先
FOLDER = "logs"
DATE_STR = datetime.utcnow().strftime("%Y-%m-%d_%H%M")

# 各URL
AP_URL = "https://apnews.com/apf-topnews"
INVESTOPEDIA_URL = "https://www.investopedia.com/news/"
REUTERS_URL = "https://www.reuters.com/world/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def collect_rss():
    os.makedirs(FOLDER, exist_ok=True)
    all_entries = []

    # --- AP通信 ---
    try:
        print(f"[AP] fetching {AP_URL}")
        resp = requests.get(AP_URL, headers=HEADERS)
        soup = BeautifulSoup(resp.content, "html.parser")
        links = soup.select('a[data-key="card-headline"]')
        print(f"[AP] {len(links)} entries retrieved")

        seen = set()
        for i, a in enumerate(links):
            href = a.get("href")
            title = a.get_text(strip=True)
            if not href or not title:
                continue
            url = f"https://apnews.com{href}" if href.startswith("/") else href
            if url in seen:
                continue
            seen.add(url)
            all_entries.append({
                "site": "Associated Press",
                "rank": i + 1,
                "title": title,
                "link": url
            })
            if i >= 19:
                break
    except Exception as e:
        print(f"[AP ERROR] {e}")

    # --- Investopedia ---
    try:
        print(f"[Investopedia] fetching {INVESTOPEDIA_URL}")
        resp = requests.get(INVESTOPEDIA_URL, headers=HEADERS)
        soup = BeautifulSoup(resp.content, "html.parser")
        links = soup.select("a.card-item__title")
        print(f"[Investopedia] {len(links)} entries retrieved")

        seen = set()
        for i, a in enumerate(links):
            href = a.get("href")
            title = a.get_text(strip=True)
            if not href or not title:
                continue
            url = href if href.startswith("http") else f"https://www.investopedia.com{href}"
            if url in seen:
                continue
            seen.add(url)
            all_entries.append({
                "site": "Investopedia",
                "rank": i + 1,
                "title": title,
                "link": url
            })
            if i >= 19:
                break
    except Exception as e:
        print(f"[Investopedia ERROR] {e}")

    # --- Reuters ---
    try:
        print(f"[Reuters] fetching {REUTERS_URL}")
        resp = requests.get(REUTERS_URL, headers=HEADERS)
        soup = BeautifulSoup(resp.content, "html.parser")
        links = soup.select('a[data-testid="Heading"]')
        print(f"[Reuters] {len(links)} entries retrieved")

        seen = set()
        for i, a in enumerate(links):
            href = a.get("href")
            title = a.get_text(strip=True)
            if not href or not title:
                continue
            url = f"https://www.reuters.com{href}" if href.startswith("/") else href
            if url in seen:
                continue
            seen.add(url)
            all_entries.append({
                "site": "Reuters",
                "rank": i + 1,
                "title": title,
                "link": url
            })
            if i >= 19:
                break
    except Exception as e:
        print(f"[Reuters ERROR] {e}")

    # 保存
    df = pd.DataFrame(all_entries)
    path = f"{FOLDER}/rss_{DATE_STR}.csv"
    df.to_csv(path, index=False)
    print(f"✅ Saved {len(all_entries)} items ➜ {path}")

if __name__ == "__main__":
    collect_rss()


