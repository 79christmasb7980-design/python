"""
네이버 금융 편입종목상위 데이터 크롤링
======================================

이 코드는 BeautifulSoup을 사용하여 네이버 금융에서 다양한 지수 정보를 
크롤링하는 예제입니다.

📌 필수 라이브러리:
   - requests
   - beautifulsoup4

💾 설치 방법:
   pip install requests beautifulsoup4

🌐 사용 가능한 지수 코드:
   - KPI200: 코스피200
   - KOSPI: 코스피
   - KOSDAQ: 코스닥
   - KOSPI100: 코스피100
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime


class NaverStockCrawler:
    """네이버 금융 크롤러 클래스"""
    
    def __init__(self):
        self.base_url = "https://finance.naver.com/sise/sise_index.naver"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_html(self, code):
        """HTML 페이지 가져오기"""
        try:
            response = requests.get(
                f"{self.base_url}?code={code}",
                headers=self.headers,
                timeout=10
            )
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                return response.content
            else:
                raise Exception(f"HTTP {response.status_code}")
        
        except Exception as e:
            print(f"❌ 요청 실패: {e}")
            return None
    
    def parse_tables(self, html_content):
        """HTML에서 테이블 추출"""
        soup = BeautifulSoup(html_content, 'html.parser')
        tables = soup.find_all('table')
        
        parsed_data = []
        
        for table_idx, table in enumerate(tables):
            rows = table.find_all('tr')
            
            if not rows:
                continue
            
            # 헤더 추출
            header_row = rows[0]
            headers = [
                th.get_text(strip=True)
                for th in header_row.find_all(['th', 'td'])
            ]
            
            # 데이터 행 추출
            data_rows = []
            for row in rows[1:]:
                cells = row.find_all('td')
                if cells:
                    row_data = [
                        cell.get_text(strip=True)
                        for cell in cells
                    ]
                    if any(row_data):  # 빈 행 제외
                        data_rows.append(row_data)
            
            # 테이블 정보 저장
            if headers or data_rows:
                parsed_data.append({
                    'table_index': table_idx,
                    'headers': headers,
                    'data': data_rows
                })
        
        return parsed_data
    
    def crawl(self, code):
        """크롤링 실행"""
        print(f"🔍 {code} 크롤링 중...")
        
        html = self.fetch_html(code)
        if html is None:
            return None
        
        parsed = self.parse_tables(html)
        
        return {
            'code': code,
            'timestamp': datetime.now().isoformat(),
            'tables': parsed
        }
    
    def print_result(self, result):
        """결과 출력"""
        if not result:
            print("❌ 결과가 없습니다.\n")
            return
        
        print("\n" + "="*90)
        print(f"📊 {result['code']} - {result['timestamp']}")
        print("="*90 + "\n")
        
        for table in result['tables']:
            print(f"📋 테이블 #{table['table_index']}")
            
            # 헤더 출력
            if table['headers']:
                print(f"    컬럼: {' | '.join(table['headers'])}")
            
            # 데이터 출력
            print(f"    데이터 ({len(table['data'])}행):")
            for i, row in enumerate(table['data'][:10], 1):  # 처음 10행만 표시
                print(f"      {i:2d}. {' | '.join(row)}")
            
            if len(table['data']) > 10:
                print(f"      ... 외 {len(table['data']) - 10}행")
            
            print()
    
    def export_json(self, result, filename):
        """JSON으로 내보내기"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"✅ JSON 저장: {filename}")
        except Exception as e:
            print(f"❌ JSON 저장 실패: {e}")
    
    def export_csv(self, result, filename):
        """CSV로 내보내기"""
        import csv
        
        try:
            for table in result['tables']:
                csv_file = filename.replace(
                    '.csv',
                    f"_table{table['table_index']}.csv"
                )
                
                with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    
                    # 헤더
                    if table['headers']:
                        writer.writerow(table['headers'])
                    
                    # 데이터
                    writer.writerows(table['data'])
                
                print(f"✅ CSV 저장: {csv_file}")
        
        except Exception as e:
            print(f"❌ CSV 저장 실패: {e}")


# ============================================================
# 사용 예제
# ============================================================

def main():
    """메인 함수"""
    
    # 크롤러 생성
    crawler = NaverStockCrawler()
    
    # 크롤링할 지수 코드 목록
    codes = ["KPI200", "KOSPI", "KOSDAQ"]
    
    print("="*90)
    print("🌐 네이버 금융 데이터 크롤링")
    print("="*90 + "\n")
    
    all_results = []
    
    # 각 지수 크롤링
    for code in codes:
        result = crawler.crawl(code)
        
        if result:
            crawler.print_result(result)
            all_results.append(result)
            
            # 개별 저장
            crawler.export_json(result, f"stock_data_{code}.json")
            crawler.export_csv(result, f"stock_data_{code}.csv")
    
    # 전체 결과 저장
    if all_results:
        with open("stock_data_all.json", 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"✅ 전체 데이터 저장: stock_data_all.json")
    
    print("\n✅ 모든 작업 완료!\n")


if __name__ == "__main__":
    main()
