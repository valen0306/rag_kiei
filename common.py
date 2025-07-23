import requests
from bs4 import BeautifulSoup, Tag
import re
import json
import os

def get_page_content(url):
    """指定されたURLのページコンテンツを取得"""
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

def extract_text_from_table(soup, section_title):
    """指定されたセクションタイトルのテーブルからテキストを抽出"""
    h4 = soup.find("h4", string=section_title)
    if h4:
        table = h4.find_next_sibling("table")
        if table and isinstance(table, Tag):
            tds = table.find_all("td")
            if tds:
                texts = []
                for td in tds:
                    if isinstance(td, Tag):
                        text = td.get_text(separator='\n', strip=True)
                        if text:
                            texts.append(text)
                return '\n'.join(texts)
    return None

def save_to_json(data, filename):
    """データをJSONファイルに保存"""
    # ディレクトリが存在しない場合はエラーを発生
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        raise FileNotFoundError(f"ディレクトリ '{directory}' が存在しません。事前に作成してください。")
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"データを {filename} に保存しました")

def print_progress(current, total, message=""):
    """進捗を表示"""
    print(f"{message}: {current}/{total}") 