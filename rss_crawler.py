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

    df = pd.DataFrame(all_entries)
    df.to_csv(f"{FOLDER}/rss_{DATE_STR}.csv", index=False)
    print(f"✅ Saved {len(all_entries)} items ➜ logs/rss_{DATE_STR}.csv")

if __name__ == "__main__":
    collect_rss()
