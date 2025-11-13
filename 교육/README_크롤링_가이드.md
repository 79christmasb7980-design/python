# 네이버 금융 편입종목상위 데이터 크롤링 가이드

네이버 금융 페이지에서 **BeautifulSoup**을 사용하여 편입종목상위 데이터를 크롤링하는 방법을 설명합니다.

## 📌 개요

- **대상 URL**: `https://finance.naver.com/sise/sise_index.naver?code=KPI200`
- **데이터**: 코스피200(KPI200)의 지수정보 및 종목 데이터
- **라이브러리**: BeautifulSoup4, requests

---

## 🔧 설치 및 준비

### 1. 필수 라이브러리 설치

```bash
pip install requests beautifulsoup4
```

### 2. Python 3.6 이상 필요

```bash
python --version
```

---

## 📖 기본 크롤링 코드

### 간단한 버전 (15줄)

```python
import requests
from bs4 import BeautifulSoup

# URL과 헤더 설정
url = "https://finance.naver.com/sise/sise_index.naver?code=KPI200"
headers = {'User-Agent': 'Mozilla/5.0'}

# 페이지 요청
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'

# HTML 파싱
soup = BeautifulSoup(response.content, 'html.parser')

# 테이블 찾기
tables = soup.find_all('table')

# 각 테이블의 데이터 추출
for idx, table in enumerate(tables):
    rows = table.find_all('tr')
    
    print(f"\n=== 테이블 #{idx} ===")
    
    # 헤더 출력
    if rows:
        headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
        print(f"헤더: {headers}")
    
    # 데이터 행 출력
    print("데이터:")
    for row in rows[1:]:
        cells = [td.get_text(strip=True) for td in row.find_all('td')]
        if cells:
            print(cells)
```

---

## 📊 중급 버전 (클래스 기반)

```python
import requests
from bs4 import BeautifulSoup
import csv


class NaverStockCrawler:
    """네이버 금융 크롤러"""
    
    def __init__(self):
        self.base_url = "https://finance.naver.com/sise/sise_index.naver"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def crawl(self, code):
        """지수 데이터 크롤링"""
        try:
            url = f"{self.base_url}?code={code}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.content, 'html.parser')
            tables = soup.find_all('table')
            
            results = []
            for table in tables:
                table_data = {
                    'headers': [],
                    'rows': []
                }
                
                rows = table.find_all('tr')
                
                # 헤더
                if rows:
                    table_data['headers'] = [
                        th.get_text(strip=True) 
                        for th in rows[0].find_all(['th', 'td'])
                    ]
                
                # 데이터
                for row in rows[1:]:
                    cells = row.find_all('td')
                    if cells:
                        row_data = [cell.get_text(strip=True) for cell in cells]
                        if any(row_data):
                            table_data['rows'].append(row_data)
                
                results.append(table_data)
            
            return results
        
        except Exception as e:
            print(f"에러: {e}")
            return None
    
    def save_csv(self, data, filename):
        """CSV로 저장"""
        for idx, table in enumerate(data):
            csv_file = filename.replace('.csv', f'_table{idx}.csv')
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                if table['headers']:
                    writer.writerow(table['headers'])
                writer.writerows(table['rows'])
            print(f"저장: {csv_file}")


# 사용 예제
if __name__ == "__main__":
    crawler = NaverStockCrawler()
    
    # 크롤링
    data = crawler.crawl("KPI200")
    
    # 출력
    for table in data:
        print(f"헤더: {table['headers']}")
        for row in table['rows'][:5]:
            print(row)
        print()
    
    # CSV 저장
    crawler.save_csv(data, "kospi200.csv")
```

---

## 🎯 주요 사용 방법

### 1. 특정 지수 코드로 크롤링

```python
# 코스피200
data = crawler.crawl("KPI200")

# 코스피
data = crawler.crawl("KOSPI")

# 코스닥
data = crawler.crawl("KOSDAQ")

# 코스피100
data = crawler.crawl("KOSPI100")
```

### 2. 데이터 필터링

```python
# 특정 종목 찾기
for row in data[1]['rows']:  # 두 번째 테이블의 종목 데이터
    if '삼성' in row[1]:  # 2번째 열에서 삼성 검색
        print(row)
```

### 3. 데이터 분석

```python
# 가격 기준 정렬
def get_price(row):
    try:
        return int(row[2].replace(',', ''))
    except:
        return 0

data[1]['rows'].sort(key=get_price, reverse=True)
```

---

## ⚠️ 주의사항

### 1. User-Agent 필수
네이버는 User-Agent 검증을 하므로 반드시 설정해야 합니다.

```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
```

### 2. 타임아웃 설정
네트워크 지연에 대비하여 타임아웃을 설정합니다.

```python
response = requests.get(url, headers=headers, timeout=10)
```

### 3. 인코딩 설정
한글 텍스트를 올바르게 처리하기 위해 UTF-8 인코딩을 설정합니다.

```python
response.encoding = 'utf-8'
```

### 4. 너무 많은 요청 금지
짧은 시간에 여러 번 요청하면 차단될 수 있습니다.

```python
import time
time.sleep(1)  # 1초 대기
```

---

## 🔄 Selenium을 사용한 동적 페이지 크롤링

JavaScript로 렌더링되는 콘텐츠가 필요한 경우 Selenium을 사용합니다.

### 설치

```bash
pip install selenium
```

### 코드 예제

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import time

# Chrome 드라이버 설정
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 백그라운드 실행

driver = webdriver.Chrome(options=options)

try:
    # 페이지 로드
    url = "https://finance.naver.com/sise/sise_index.naver?code=KPI200"
    driver.get(url)
    
    # JavaScript 로딩 대기
    time.sleep(3)
    
    # BeautifulSoup으로 파싱
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # 테이블 추출
    tables = soup.find_all('table')
    # ... 이후 처리
finally:
    driver.quit()
```

---

## 📈 실행 결과 예시

```
==========================================================================================
📊 KPI200 - 2025-11-13T10:10:28.148211
==========================================================================================

📋 테이블 #0
    컬럼: 코스피200 | 587.88 |  | 상한종목수 | 0
    데이터 (6행):
       1. 1.15 |  | 78
       2. +0.20% |  | 0
       3. 588.28 |  | 116
       4. 582.82 |  | 5

📋 테이블 #1
    컬럼:  | 삼성전자 | 103,700 |
    데이터 (4행):
       1.  | SK하이닉스 | 615,000 |
       2.  | 에이비엘바이오 | 164,000 |
       3.  | 두산에너빌리티 | 80,400 |
       4.  | 한화오션 | 124,900 |

✅ JSON 저장: stock_data_KPI200.json
✅ CSV 저장: stock_data_KPI200_table0.csv
```

---

## 🛠️ 문제 해결

### Q1: "ModuleNotFoundError: No module named 'requests'"

**해결방법:**
```bash
pip install requests beautifulsoup4
```

### Q2: 한글 깨짐 문제

**해결방법:**
```python
response.encoding = 'utf-8'
```

### Q3: 데이터가 로드되지 않음 (JavaScript 렌더링)

**해결방법:**
Selenium 사용으로 변경

```python
from selenium import webdriver
# 위의 Selenium 예제 참조
```

### Q4: 요청 거부 (403 Forbidden)

**해결방법:**
헤더에 Referer 추가

```python
headers = {
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://finance.naver.com/'
}
```

---

## 📚 참고 자료

- [BeautifulSoup 공식 문서](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [requests 공식 문서](https://docs.python-requests.org/)
- [Selenium 공식 문서](https://selenium-python.readthedocs.io/)

---

## ✅ 체크리스트

- [ ] Python 3.6 이상 설치 확인
- [ ] `requests`, `beautifulsoup4` 설치 확인
- [ ] 기본 크롤링 코드 실행 성공
- [ ] CSV 파일로 저장 성공
- [ ] 데이터 분석/필터링 완료

---

**작성일**: 2025년 11월 13일  
**마지막 수정**: 2025년 11월 13일
