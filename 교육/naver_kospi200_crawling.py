"""
네이버 금융 - 코스피200 편입종목상위 데이터 크롤링
URL: https://finance.naver.com/sise/sise_index.naver?code=KPI200
"""

import requests
from bs4 import BeautifulSoup
import re

# URL 설정
url = "https://finance.naver.com/sise/sise_index.naver?code=KPI200"

# 헤더 설정 (User-Agent 필수)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def crawl_top_items():
    """
    편입종목상위 데이터를 크롤링하는 함수
    """
    try:
        print("📡 페이지 요청 중...\n")
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"✗ 요청 실패: {response.status_code}")
            return None
        
        print("✓ 페이지 로드 성공\n")
        
        # BeautifulSoup으로 파싱
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 편입종목상위 섹션 찾기
        # 보통 "편입종목상위"라는 텍스트를 포함한 헤딩 찾기
        target_section = None
        
        # 방법 1: h2나 h3 태그에서 "편입" 텍스트 찾기
        for heading in soup.find_all(['h2', 'h3', 'h4']):
            if '편입' in heading.get_text():
                print(f"섹션 제목 발견: {heading.get_text()}")
                target_section = heading
                break
        
        # 방법 2: div나 section 태그의 class나 id에서 찾기
        if not target_section:
            for elem in soup.find_all('div', class_=True):
                if '편입' in elem.get_text()[:200]:  # 처음 200자만 확인
                    text = elem.get_text(strip=True)
                    if '편입종목상위' in text:
                        target_section = elem
                        print(f"섹션 div 발견: {text[:100]}")
                        break
        
        # 방법 3: 모든 테이블 확인
        print("\n━━━ 모든 테이블 분석 ━━━\n")
        tables = soup.find_all('table')
        
        for idx, table in enumerate(tables):
            rows = table.find_all('tr')
            
            if len(rows) == 0:
                continue
            
            # 첫 번째 행 (헤더)
            first_row_cells = rows[0].find_all(['th', 'td'])
            headers_list = [cell.get_text(strip=True) for cell in first_row_cells]
            
            # 편입종목이나 상위 관련 키워드 포함 여부 확인
            header_text = ' '.join(headers_list)
            
            print(f"테이블 #{idx}")
            print(f"헤더: {headers_list}")
            
            # 데이터 행 출력
            print("데이터 행:")
            data_rows = []
            for i, row in enumerate(rows[1:11]):  # 처음 10개 행
                cols = row.find_all('td')
                if cols:
                    row_data = [col.get_text(strip=True) for col in cols]
                    data_rows.append(row_data)
                    print(f"  {i+1}: {row_data}")
            
            print()
            
            # 편입종목상위 테이블인지 판단
            # 보통 종목명, 편입률(%) 등의 열이 있음
            if any(keyword in header_text for keyword in ['종목', '편입', '비중', '가격', '변동']):
                print(f"→ 테이블 #{idx}가 편입종목상위 데이터로 보입니다!\n")
                return {
                    'headers': headers_list,
                    'data': data_rows,
                    'table_index': idx
                }
        
        return None
        
    except Exception as e:
        print(f"✗ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
        return None


def print_results(results):
    """
    크롤링 결과를 정리해서 출력
    """
    if not results:
        print("편입종목상위 데이터를 찾을 수 없습니다.")
        return
    
    print("━━━ 편입종목상위 데이터 ━━━\n")
    
    headers = results['headers']
    data = results['data']
    
    # 테이블 형식으로 출력
    print(f"컬럼: {' | '.join(headers)}")
    print("-" * 100)
    
    for row in data:
        print(" | ".join(row))


if __name__ == "__main__":
    results = crawl_top_items()
    
    if results:
        print_results(results)
        print(f"\n✓ 수집된 종목 개수: {len(results['data'])}")
    else:
        print("\n❌ 데이터 수집 실패")
