import requests
from bs4 import BeautifulSoup

# URL 설정
url = "https://finance.naver.com/sise/sise_index.naver?code=KPI200"

# 헤더 설정 (User-Agent 필수)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    # 요청 전송
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = 'utf-8'
    
    if response.status_code == 200:
        print("✓ 페이지 로드 성공")
        
        # BeautifulSoup으로 파싱
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 편입종목상위 섹션 찾기
        # 일반적으로 테이블로 구성되어 있음
        
        # 방법 1: 모든 테이블 찾기
        tables = soup.find_all('table')
        print(f"\n발견된 테이블 개수: {len(tables)}")
        
        # 방법 2: 편입종목상위 섹션 찾기
        # 제목이나 특정 텍스트를 포함하는 섹션 찾기
        
        # 편입종목 데이터 저장
        top_items_data = []
        
        # 모든 테이블 확인
        for idx, table in enumerate(tables):
            # 테이블의 첫 번째 행 확인 (제목 확인용)
            first_row = table.find('tr')
            if first_row:
                headers_in_table = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])[:3]]
                print(f"\n테이블 {idx}: {headers_in_table}")
                
                # 각 테이블의 내용 출력
                rows = table.find_all('tr')[1:]  # 헤더 제외
                for row in rows[:5]:  # 처음 5개만 확인
                    cols = row.find_all('td')
                    if cols:
                        row_data = [col.get_text(strip=True) for col in cols]
                        print(f"  데이터: {row_data[:3]}")
        
        # 편입종목상위 테이블 크롤링
        # 페이지 구조에 따라 조정 필요
        print("\n\n=== 편입종목상위 데이터 크롤링 ===\n")
        
        # id나 class가 있는 특정 섹션 찾기
        sections = soup.find_all(['div', 'section'], class_=True)
        for section in sections:
            if '편입' in section.get_text() or '편입종목' in section.get_text():
                print(f"섹션 발견: {section.get_text()[:100]}")
                
                # 해당 섹션 내의 테이블 찾기
                table = section.find('table')
                if table:
                    rows = table.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        if cols:
                            row_data = [col.get_text(strip=True) for col in cols]
                            print(row_data)
    
    else:
        print(f"✗ 요청 실패: {response.status_code}")

except Exception as e:
    print(f"✗ 에러 발생: {e}")
