"""
네이버 금융 - 코스피200 편입종목상위 데이터 크롤링
URL: https://finance.naver.com/sise/sise_index.naver?code=KPI200

작성일: 2025년 11월
설명: BeautifulSoup과 Selenium을 활용한 웹 크롤링 예제
"""

import requests
from bs4 import BeautifulSoup
import json
from typing import List, Dict
import time


class NaverFinanceCrawler:
    """네이버 금융 페이지 크롤러"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.base_url = "https://finance.naver.com/sise/sise_index.naver"
    
    def crawl_with_beautifulsoup(self, code: str = "KPI200") -> List[Dict]:
        """
        BeautifulSoup을 사용하여 코스피200 페이지 크롤링
        
        Args:
            code: 지수 코드 (기본값: KPI200 = 코스피200)
        
        Returns:
            테이블 데이터 리스트
        """
        try:
            print(f"📡 BeautifulSoup으로 {code} 페이지 요청 중...\n")
            
            response = requests.get(
                f"{self.base_url}?code={code}",
                headers=self.headers,
                timeout=10
            )
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"✗ 요청 실패: {response.status_code}")
                return []
            
            print("✓ 페이지 로드 성공\n")
            
            # HTML 파싱
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 테이블 추출
            tables = soup.find_all('table')
            print(f"발견된 테이블: {len(tables)}개\n")
            
            all_data = []
            
            for idx, table in enumerate(tables):
                rows = table.find_all('tr')
                
                if len(rows) < 2:
                    continue
                
                # 헤더 추출
                header_row = rows[0]
                headers_list = [
                    cell.get_text(strip=True) 
                    for cell in header_row.find_all(['th', 'td'])
                ]
                
                print(f"━━━ 테이블 #{idx} ━━━")
                print(f"헤더: {headers_list}")
                print("데이터:")
                
                table_data = {
                    'table_index': idx,
                    'headers': headers_list,
                    'rows': []
                }
                
                # 데이터 행 추출
                for row_idx, row in enumerate(rows[1:], 1):
                    cols = row.find_all('td')
                    if cols:
                        row_data = []
                        for col in cols:
                            # 링크가 있으면 텍스트만 추출
                            link = col.find('a')
                            text = link.get_text(strip=True) if link else col.get_text(strip=True)
                            row_data.append(text)
                        
                        if any(row_data):  # 빈 행 제외
                            table_data['rows'].append(row_data)
                            print(f"  {row_idx}: {row_data}")
                
                print()
                all_data.append(table_data)
            
            return all_data
        
        except requests.exceptions.RequestException as e:
            print(f"✗ 요청 에러: {e}")
            return []
        except Exception as e:
            print(f"✗ 예기치 않은 에러: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def crawl_with_selenium(self, code: str = "KPI200") -> List[Dict]:
        """
        Selenium을 사용하여 JavaScript 동적 로딩 포함 크롤링
        (설치 필요: pip install selenium)
        
        Args:
            code: 지수 코드
        
        Returns:
            테이블 데이터 리스트
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            print(f"📡 Selenium으로 {code} 페이지 요청 중...\n")
            
            # Chrome 옵션 설정
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')  # 백그라운드 실행
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            
            driver = webdriver.Chrome(options=options)
            
            try:
                # 페이지 로드
                url = f"{self.base_url}?code={code}"
                print(f"🔗 URL: {url}\n")
                
                driver.get(url)
                
                # JavaScript 로딩 대기 (최대 10초)
                print("⏳ JavaScript 로딩 대기 중...")
                WebDriverWait(driver, 10).until(
                    lambda driver: driver.execute_script(
                        'return document.readyState'
                    ) == 'complete'
                )
                time.sleep(2)  # 추가 로딩 시간
                
                print("✓ 페이지 로드 완료\n")
                
                # 페이지 소스 추출
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # 테이블 추출
                tables = soup.find_all('table')
                print(f"발견된 테이블: {len(tables)}개\n")
                
                all_data = []
                
                for idx, table in enumerate(tables):
                    rows = table.find_all('tr')
                    
                    if len(rows) < 2:
                        continue
                    
                    # 헤더 추출
                    header_row = rows[0]
                    headers_list = [
                        cell.get_text(strip=True)
                        for cell in header_row.find_all(['th', 'td'])
                    ]
                    
                    print(f"━━━ 테이블 #{idx} ━━━")
                    print(f"헤더: {headers_list}")
                    print("데이터:")
                    
                    table_data = {
                        'table_index': idx,
                        'headers': headers_list,
                        'rows': []
                    }
                    
                    # 데이터 행 추출
                    for row_idx, row in enumerate(rows[1:], 1):
                        cols = row.find_all('td')
                        if cols:
                            row_data = [col.get_text(strip=True) for col in cols]
                            
                            if any(row_data):
                                table_data['rows'].append(row_data)
                                print(f"  {row_idx}: {row_data}")
                    
                    print()
                    all_data.append(table_data)
                
                return all_data
            
            finally:
                driver.quit()
        
        except ImportError:
            print("⚠️  Selenium이 설치되지 않았습니다.")
            print("설치 명령어: pip install selenium")
            print("또한 ChromeDriver를 다운로드해야 합니다.")
            return []
        except Exception as e:
            print(f"✗ Selenium 에러: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def save_to_json(self, data: List[Dict], filename: str = "kospi200_data.json"):
        """
        수집한 데이터를 JSON 파일로 저장
        
        Args:
            data: 저장할 데이터
            filename: 저장 파일명
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✓ 데이터 저장 완료: {filename}")
        except Exception as e:
            print(f"✗ 저장 실패: {e}")
    
    def save_to_csv(self, data: List[Dict], filename: str = "kospi200_data.csv"):
        """
        수집한 데이터를 CSV 파일로 저장
        
        Args:
            data: 저장할 데이터
            filename: 저장 파일명
        """
        try:
            import csv
            
            for table_idx, table in enumerate(data):
                csv_filename = filename.replace('.csv', f'_table{table_idx}.csv')
                
                with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    # 헤더 작성
                    writer.writerow(table['headers'])
                    # 데이터 작성
                    writer.writerows(table['rows'])
                
                print(f"✓ CSV 저장 완료: {csv_filename}")
        except Exception as e:
            print(f"✗ CSV 저장 실패: {e}")
    
    def print_results(self, data: List[Dict], method: str = "BeautifulSoup"):
        """
        크롤링 결과 출력
        
        Args:
            data: 크롤링 데이터
            method: 크롤링 방법
        """
        if not data:
            print("❌ 수집된 데이터가 없습니다.")
            return
        
        print(f"\n{'='*80}")
        print(f"크롤링 결과 (방법: {method})")
        print(f"{'='*80}\n")
        
        for table in data:
            idx = table['table_index']
            headers = table['headers']
            rows = table['rows']
            
            print(f"📊 테이블 #{idx}")
            print(f"행 개수: {len(rows)}")
            print(f"컬럼: {', '.join(headers)}")
            print("-" * 100)
            
            for row in rows:
                print(" | ".join(row))
            
            print("\n")


def main():
    """메인 함수"""
    
    crawler = NaverFinanceCrawler()
    
    print("="*80)
    print("네이버 금융 - 코스피200(KPI200) 데이터 크롤링")
    print("="*80 + "\n")
    
    # 방법 1: BeautifulSoup 사용 (항상 실행 가능)
    print("\n[방법 1] BeautifulSoup 사용")
    print("-" * 80)
    results_bs = crawler.crawl_with_beautifulsoup("KPI200")
    crawler.print_results(results_bs, "BeautifulSoup")
    
    # 결과 저장
    if results_bs:
        crawler.save_to_json(results_bs, "kospi200_beautifulsoup.json")
        crawler.save_to_csv(results_bs, "kospi200_beautifulsoup.csv")
    
    # 방법 2: Selenium 사용 (선택사항)
    # 주석 제거하고 Selenium 설치 후 사용 가능
    """
    print("\n[방법 2] Selenium 사용")
    print("-" * 80)
    results_selenium = crawler.crawl_with_selenium("KPI200")
    crawler.print_results(results_selenium, "Selenium")
    
    if results_selenium:
        crawler.save_to_json(results_selenium, "kospi200_selenium.json")
        crawler.save_to_csv(results_selenium, "kospi200_selenium.csv")
    """
    
    print("\n✓ 크롤링 작업 완료!")


if __name__ == "__main__":
    main()
