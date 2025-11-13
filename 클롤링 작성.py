import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import time

def fetch_html(url, headers=None, timeout=10):
    if headers is None:
        headers = {
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/120.0.0.0 Safari/537.36")
        }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.text

def extract_titles_from_soup(soup):
    titles = []

    # 여러 가능한 뉴스 타이틀 셀렉터를 시도
    selectors = [
        # 사용자가 제공한 특정 클래스 조합 (이미지+텍스트 컴포넌트 내부 링크)
        "a.jyxwDwu8umzdhCQxX48l.fds-comps-right-image-text-title",
        # 해당 링크 내부에 제목 텍스트가 들어있는 span
        "a.jyxwDwu8umzdhCQxX48l.fds-comps-right-image-text-title span.fds-comps-text",
        "a.news_tit",        # 네이버 뉴스 검색 (뉴스탭) 타이틀
        "a._sp_each_title",  # 검색 결과의 개별 타이틀(과거/다른 형식)
        "a.tit",             # 일부 결과에서 사용
        "a.title",           # 보편적인 이름
        "a.article",         # 드물게 사용
        "a.link_tit",        # 드물게 사용
        "div.news_area a"    # 대체 경로
    ]

    for sel in selectors:
        for el in soup.select(sel):
            # selector가 a 태그를 바로 가리킬 수도 있고, 내부 span을 가리킬 수도 있음
            if el.name == 'a':
                # 먼저 내부 span.fds-comps-text가 있으면 그 텍스트 우선
                sp = el.select_one('span.fds-comps-text')
                if sp and sp.get_text(strip=True):
                    titles.append(sp.get_text(strip=True))
                    continue
                # 없으면 a 태그 텍스트 사용
                text = el.get_text(strip=True)
                if text:
                    titles.append(text)
            else:
                # el이 span 등 a가 아닌 경우 텍스트 직접 사용
                text = el.get_text(strip=True)
                if text:
                    titles.append(text)

    # 추가 안전망: <a> 태그 중 속성으로 기사 링크가 있을 때 텍스트를 수집
    if not titles:
        for a in soup.find_all("a"):
            # 보통 뉴스 링크는 'news'나 'nid' 같은 키워드를 가지기도 함
            href = a.get("href", "")
            if "news" in href or "nid" in href:
                t = a.get_text(strip=True)
                if t:
                    titles.append(t)

    # 중복 제거 및 깔끔하게 정리
    unique = []
    seen = set()
    for t in titles:
        if t not in seen:
            unique.append(t)
            seen.add(t)
    return unique

def crawl_naver_search_titles(url, save_to=None, delay=0.5):
    """
    주어진 네이버 검색 URL에서 기사 제목들을 추출합니다.
    - url: 네이버 검색 결과 URL (예: 사용자가 준 URL)
    - save_to: 파일 경로로 지정하면 결과를 텍스트 파일로 저장
    - delay: 요청 전후 대기 시간(초) — 과도한 요청을 막기 위해 사용
    """
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")
    titles = extract_titles_from_soup(soup)

    if save_to:
        with open(save_to, "w", encoding="utf-8") as f:
            for t in titles:
                f.write(t + "\n")

    return titles

if __name__ == "__main__":
    # 예시 URL: 사용자가 제공한 URL을 그대로 붙여넣어 사용하세요.
    url = ("https://search.naver.com/search.naver?where=nexearch&sm=top_hty&"
           "fbm=0&ie=utf8&query=%EC%95%84%EC%9D%B4%ED%8F%B017&ackey=j7mkbobm")

    titles = crawl_naver_search_titles(url, save_to="naver_titles.txt", delay=0.5)

    if titles:
        print(f"총 {len(titles)}개의 제목을 찾았습니다:")
        for i, t in enumerate(titles, 1):
            print(f"{i}. {t}")
    else:
        print("제목을 찾지 못했습니다. (동적로딩/셀레니움 필요 가능성 있음)")