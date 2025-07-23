import re
from common import get_page_content, extract_text_from_table, save_to_json, print_progress

class SafetySiteScraper:
    def __init__(self, gyosyu=3):
        self.gyosyu = gyosyu
        self.base_url = "https://anzeninfo.mhlw.go.jp/anzen_pg/SAI_LST.aspx"
        self.detail_base_url = "https://anzeninfo.mhlw.go.jp/anzen_pg/SAI_DET.aspx"
    
    def get_total_pages(self):
        """総ページ数を取得"""
        url = f"{self.base_url}?gyosyu={self.gyosyu}"
        print(f"URL: {url}")
        soup = get_page_content(url)
        
        # 「1/48ページ」などの表記を探す
        page_info = soup.find(string=re.compile(r"\d+/\d+ページ"))
        if page_info:
            match = re.search(r"/(\d+)ページ", str(page_info))
            if match:
                total_pages = int(match.group(1))
                print(f"総ページ数: {total_pages}")
                return total_pages
        
        print("ページ数が見つかりませんでした。")
        return None
    
    def get_case_ids_from_page(self, page_num):
        """指定ページから事例IDを取得"""
        url = f"{self.base_url}?gyosyu={self.gyosyu}&page={page_num}"
        soup = get_page_content(url)
        
        case_ids = []
        # aタグのhref属性に"javascript:f_page_send(数字)"が含まれるものを探す
        for a in soup.find_all("a", href=True):
            match = re.match(r"javascript:f_page_send\((\d+)\)", a["href"])
            if match:
                case_ids.append(int(match.group(1)))
        return case_ids
    
    def get_all_case_ids(self):
        """全ページから事例IDを取得"""
        total_pages = self.get_total_pages()
        if total_pages is None:
            print("ページ数が取得できませんでした。")
            return []
        
        all_case_ids = []
        for page in range(1, total_pages + 1):
            print_progress(page, total_pages, "ページ取得中")
            case_ids = self.get_case_ids_from_page(page)
            all_case_ids.extend(case_ids)
        return all_case_ids
    
    def get_case_detail(self, case_id):
        """事例の詳細情報を取得"""
        url = f"{self.detail_base_url}?joho_no={case_id}"
        soup = get_page_content(url)
        
        return {
            "id": case_id,
            "発生状況": extract_text_from_table(soup, "発生状況"),
            "原因": extract_text_from_table(soup, "原因"),
            "対策": extract_text_from_table(soup, "対策"),
        }
    
    def get_all_case_details(self, case_ids):
        """全事例の詳細情報を取得"""
        details = []
        for i, case_id in enumerate(case_ids):
            print_progress(i+1, len(case_ids), f"詳細取得中 - ID: {case_id}")
            detail = self.get_case_detail(case_id)
            details.append(detail)
        return details
    
    def scrape_all(self, limit=None):
        """全データをスクレイピング"""
        print("=== 職場の安全サイト スクレイピング開始 ===")
        
        # 事例IDを取得
        case_ids = self.get_all_case_ids()
        print(f"取得した事例数: {len(case_ids)}")
        
        # 制限がある場合は適用
        if limit:
            case_ids = case_ids[:limit]
            print(f"制限により {limit} 件に絞り込みました")
        
        # 詳細情報を取得
        details = self.get_all_case_details(case_ids)
        
        # JSONファイルに保存
        filename = f"anzen_info/safety_site_data_gyosyu{self.gyosyu}.json"
        save_to_json(details, filename)
        
        return details

if __name__ == "__main__":
    scraper = SafetySiteScraper(gyosyu=3)
    # 最初の3件だけテスト
    data = scraper.scrape_all(limit=3)
    print(f"完了: {len(data)} 件のデータを取得しました") 