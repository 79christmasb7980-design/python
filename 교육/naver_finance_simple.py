"""
네이버 금융 편입종목상위 크롤링 - 간단한 버전
URL: https://finance.naver.com/sise/sise_index.naver?code=KPI200

BeautifulSoup을 사용한 간단하고 효율적인 크롤링 코드
"""

import requests
from bs4 import BeautifulSoup


def crawl_naver_finance(code="KPI200"):
    """
    네이버 금융에서 지수 정보 및 종목 데이터 크롤링
    
    Parameters:
    -----------
    code : str
        지수 코드 (기본값: KPI200 = 코스피200)
    
    Returns:
    --------
    dict : 크롤링된 데이터
    """
    
    url = f"https://finance.naver.com/sise/sise_index.naver?code={code}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print(f"🌐 {code} 크롤링 시작...")
    print(f"📍 URL: {url}\n")
    
    try:
        # 페이지 요청
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"❌ 요청 실패: {response.status_code}")
            return None
        
        # HTML 파싱
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 테이블 찾기
        tables = soup.find_all('table')
        
        results = {
            'code': code,
            'tables': []
        }
        
        # 각 테이블 처리
        for idx, table in enumerate(tables):
            table_data = {
                'index': idx,
                'headers': [],
                'rows': []
            }
            
            rows = table.find_all('tr')
            
            # 헤더 추출
            if rows:
                header_cells = rows[0].find_all(['th', 'td'])
                table_data['headers'] = [cell.get_text(strip=True) for cell in header_cells]
            
            # 데이터 행 추출
            for row in rows[1:]:
                cells = row.find_all('td')
                if cells:
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    if any(row_data):  # 빈 행 제외
                        table_data['rows'].append(row_data)
            
            results['tables'].append(table_data)
        
        return results
    
    except Exception as e:
        print(f"❌ 에러: {e}")
        return None


def display_results(data):
    """
    크롤링 결과를 보기 좋게 출력
    """
    
    if not data:
        print("데이터가 없습니다.")
        return
    
    print("="*100)
    print(f"코드: {data['code']}")
    print("="*100 + "\n")
    
    for table in data['tables']:
        print(f"📊 테이블 #{table['index']}")
        
        if table['headers']:
            print(f"헤더: {table['headers']}")
            print("-"*100)
            
            for i, row in enumerate(table['rows'], 1):
                print(f"{i:2d}. {' | '.join(row)}")
        
        print(f"총 {len(table['rows'])}개 행\n")


def save_to_csv(data, filename="output.csv"):
    """
    데이터를 CSV 파일로 저장
    """
    import csv
    
    try:
        for table in data['tables']:
            csv_file = filename.replace('.csv', f'_table{table["index"]}.csv')
            
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # 헤더 작성
                if table['headers']:
                    writer.writerow(table['headers'])
                
                # 데이터 작성
                writer.writerows(table['rows'])
            
            print(f"✅ {csv_file} 저장 완료")
    
    except Exception as e:
        print(f"❌ CSV 저장 실패: {e}")


# ============================================================
# 사용 예제
# ============================================================

if __name__ == "__main__":
    
    print("\n" + "="*100)
    print("네이버 금융 - 코스피200 크롤링")
    print("="*100 + "\n")
    
    # 1. 데이터 크롤링
    data = crawl_naver_finance("KPI200")
    
    # 2. 결과 출력
    if data:
        display_results(data)
        
        # 3. CSV로 저장 (선택사항)
        save_to_csv(data, "naver_kospi200.csv")
    
    print("\n✅ 작업 완료!\n")
