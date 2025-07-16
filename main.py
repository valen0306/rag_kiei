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

if __name__ == "__main__":
    get_total_pages()
