import requests
from bs4 import BeautifulSoup
import sys
import os

# 현재 디렉토리의 random.py와의 충돌 방지
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# URL 설정
url = "https://finance.naver.com/sise/sise_index.naver?code=KPI200"

# 헤더 설정 (User-Agent 필수)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    # 요청 전송
    print("📡 페이지 요청 중...")
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = 'utf-8'
    
    if response.status_code == 200:
        print("✓ 페이지 로드 성공\n")
        
        # BeautifulSoup으로 파싱
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 모든 테이블 찾기
        tables = soup.find_all('table')
        print(f"발견된 테이블 개수: {len(tables)}\n")
        
        # 각 테이블 분석
        for idx, table in enumerate(tables):
            rows = table.find_all('tr')
            if len(rows) > 0:
                # 첫 번째 행 (헤더)
                first_row = rows[0]
                headers_list = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])]
                
                if headers_list:
                    print(f"━━━ 테이블 {idx} ━━━")
                    print(f"헤더: {headers_list}")
                    
                    # 데이터 행 확인 (처음 3개만)
                    for i, row in enumerate(rows[1:4]):
                        cols = row.find_all('td')
                        if cols:
                            row_data = [col.get_text(strip=True) for col in cols]
                            print(f"행{i+1}: {row_data}")
                    print()
    
    else:
        print(f"✗ 요청 실패: {response.status_code}")

except Exception as e:
    print(f"✗ 에러 발생: {e}")
    import traceback
    traceback.print_exc()
