# 職場の安全サイトのスクレイピング
from safety_site import SafetySiteScraper

if __name__ == "__main__":
    # 職場の安全サイトのスクレイピング
    scraper = SafetySiteScraper(gyosyu=3)
    data = scraper.scrape_all(limit=3)  # 最初の3件だけテスト
    print(f"完了: {len(data)} 件のデータを取得しました")
