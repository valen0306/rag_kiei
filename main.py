import requests
from bs4 import BeautifulSoup, Tag
import re



def get_total_pages():
    url = "https://anzeninfo.mhlw.go.jp/anzen_pg/SAI_LST.aspx?gyosyu=3"
    print(f"url: {url}")
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # 「1/48ページ」などの表記を探す
    # 例: 1/48ページ
    page_info = soup.find(string=re.compile(r"\d+/\d+ページ"))
    if page_info:
        match = re.search(r"/(\d+)ページ", str(page_info))
        if match:
            total_pages = int(match.group(1))
            print(f"総ページ数: {total_pages}")
            return total_pages

    print("ページ数が見つかりませんでした。")
    return None

def get_case_ids_from_page(page_num):
    url = f"https://anzeninfo.mhlw.go.jp/anzen_pg/SAI_LST.aspx?gyosyu=3&page={page_num}"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    case_ids = []
    # aタグのhref属性に"javascript:f_page_send(数字)"が含まれるものを探す
    for a in soup.find_all("a", href=True):
        match = re.match(r"javascript:f_page_send\((\d+)\)", a["href"])
        if match:
            case_ids.append(int(match.group(1)))
    return case_ids

def get_all_case_ids():
    total_pages = get_total_pages()
    if total_pages is None:
        print("ページ数が取得できませんでした。")
        return []
    all_case_ids = []
    for page in range(1, total_pages + 1):
        case_ids = get_case_ids_from_page(page)
        all_case_ids.extend(case_ids)
    return all_case_ids

def get_case_detail(case_id):
    url = f"https://anzeninfo.mhlw.go.jp/anzen_pg/SAI_DET.aspx?joho_no={case_id}"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # 「発生状況」「原因」「対策」を抽出
    def extract_text(section_title):
        # h4タグでセクションタイトルを探す
        h4 = soup.find("h4", string=section_title)
        if h4:
            # h4の直後のtableを取得
            table = h4.find_next_sibling("table")
            if table and isinstance(table, Tag):
                # table内のtd要素を取得（複数のtdがある場合は全て結合）
                tds = table.find_all("td")
                if tds:
                    # 全てのtdのテキストを結合
                    texts = []
                    for td in tds:
                        if isinstance(td, Tag):
                            text = td.get_text(separator='\n', strip=True)
                            if text:
                                texts.append(text)
                    return '\n'.join(texts)
        return None

    return {
        "id": case_id,
        "発生状況": extract_text("発生状況"),
        "原因": extract_text("原因"),
        "対策": extract_text("対策"),
    }

def get_all_case_details(case_ids):
    details = []
    for i, case_id in enumerate(case_ids):
        print(f"詳細取得中: {i+1}/{len(case_ids)} - ID: {case_id}")
        detail = get_case_detail(case_id)
        details.append(detail)
    return details

if __name__ == "__main__":
    case_ids = get_all_case_ids()
    print(f"件数: {len(case_ids)}")
    print(case_ids)
    # 例として最初の3件だけ詳細を取得
    details = get_all_case_details(case_ids[:3])
    import json
    print(json.dumps(details, ensure_ascii=False, indent=2))
