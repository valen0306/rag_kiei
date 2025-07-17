import requests
from bs4 import BeautifulSoup
import re


def get_total_pages():
    url = "https://anzeninfo.mhlw.go.jp/anzen_pg/SAI_LST.aspx?gyosyu=3"
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

if __name__ == "__main__":
    case_ids = get_all_case_ids()
    print(f"件数: {len(case_ids)}")
    print(case_ids)
