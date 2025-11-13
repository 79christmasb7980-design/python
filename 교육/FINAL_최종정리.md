# 📊 네이버 금융 Top 5 종목 팝업 - 최종 완성 가이드

## 🎉 완성된 파일 목록

### 🌟 **팝업 버전 (TOP 3 추천)**

| 파일 | 설명 | 실행 명령어 | 특징 |
|------|------|-----------|------|
| **stock_popup_gui.py** | GUI 팝업 (⭐ 가장 권장) | `python stock_popup_gui.py` | 깔끔한 UI, 여러 지수 선택, 새로고침 |
| **stock_popup_simple.py** | 간단 팝업 | `python stock_popup_simple.py` | 단순하고 빠름 |
| **stock_top5_console.py** | 콘솔 팝업 | `python stock_top5_console.py` | 가장 빠르고 가벼움 |

### 📚 **학습용 버전**

| 파일 | 설명 | 특징 |
|------|------|------|
| `naver_finance_simple.py` | 함수 기반 크롤러 | 코드가 간단, 기초 학습용 |
| `naver_kospi200_complete.py` | 클래스 기반 크롤러 | 확장 가능, 중급 학습용 |
| `naver_stock_crawler.py` | 고급 크롤러 | CSV/JSON 저장, 고급 학습용 |

### 📖 **문서**

| 파일 | 내용 |
|------|------|
| `README_크롤링_가이드.md` | 기본 크롤링 가이드 |
| `TOP5_팝업_완전가이드.md` | Top 5 팝업 완전 가이드 |
| `00_README_먼저읽기.py` | 빠른 시작 & 테스트 |

### 💾 **저장된 데이터**

```
CSV 파일들:
- kospi200_beautifulsoup_table0.csv
- kospi200_beautifulsoup_table1.csv
- naver_kospi200_table0.csv
- naver_kospi200_table1.csv
- stock_data_KPI200_table0.csv
- stock_data_KPI200_table1.csv
- stock_data_KOSPI_table0.csv
- stock_data_KOSPI_table1.csv
- stock_data_KOSDAQ_table0.csv
- stock_data_KOSDAQ_table1.csv

JSON 파일들:
- kospi200_beautifulsoup.json
- stock_data_KPI200.json
- stock_data_KOSPI.json
- stock_data_KOSDAQ.json
- stock_data_all.json
```

---

## 🚀 빠른 시작 (3단계)

### 1️⃣ 라이브러리 설치 (한 번만)
```bash
pip install requests beautifulsoup4
```

### 2️⃣ 파일 선택하여 실행

**추천: GUI 팝업 버전**
```bash
python stock_popup_gui.py
```

또는 다른 버전:
```bash
python stock_popup_simple.py
python stock_top5_console.py
```

### 3️⃣ 데이터 확인
- 팝업 창이 열리면 ✅
- Top 5 종목이 표시되면 ✅

---

## 💡 각 파일 선택 가이드

### 🎯 **상황별 추천**

| 상황 | 추천 파일 | 이유 |
|------|----------|------|
| 처음 사용자 | `stock_popup_gui.py` | 직관적이고 예쁨 |
| 빠른 실행 | `stock_top5_console.py` | 가장 빠르고 가벼움 |
| 학습용 | `naver_finance_simple.py` | 코드가 간단하고 명확 |
| 데이터 저장 | `naver_stock_crawler.py` | CSV/JSON 자동 저장 |
| 고급 학습 | `naver_kospi200_complete.py` | 클래스 및 확장 기능 |

---

## 📖 사용 방법

### GUI 팝업 버전 (`stock_popup_gui.py`)

```
1. 스크립트 실행
   python stock_popup_gui.py

2. 메인 윈도우 나타남
   ┌─────────────────────┐
   │ 📈 네이버 금융 크롤러 │
   └─────────────────────┘

3. 원하는 지수 버튼 클릭
   📊 코스피200 (KPI200)
   📊 코스피 (KOSPI)
   📊 코스닥 (KOSDAQ)
   📊 코스피100 (KOSPI100)

4. 팝업 윈도우에서 Top 5 확인
   ┌──────────────────────────┐
   │ 🎯 KPI200 상위 5개 종목  │
   ├──────────────────────────┤
   │ 🥇 1 | SK하이닉스 | ₩... │
   │ 🥈 2 | 에이비엘바이오 | ..│
   │ ...                      │
   └──────────────────────────┘

5. 새로고침 또는 닫기
   🔄 새로고침  ❌ 닫기
```

### 콘솔 팝업 버전 (`stock_top5_console.py`)

```bash
# 기본 실행 (간단 표시)
python stock_top5_console.py

# 대화형 메뉴
python stock_top5_console.py -m

# 전체 지수 조회
python stock_top5_console.py -a

# 특정 지수만
python stock_top5_console.py KPI200
```

---

## 🔧 코드 설명

### 핵심 코드 (25줄)

```python
import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk

# 1. 데이터 가져오기
def get_top5(code="KPI200"):
    url = f"https://finance.naver.com/sise/sise_index.naver?code={code}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = 'utf-8'
    
    soup = BeautifulSoup(response.content, 'html.parser')
    tables = soup.find_all('table')
    
    stocks = []
    for row in tables[1].find_all('tr')[1:6]:
        cells = row.find_all('td')
        if len(cells) >= 3:
            stocks.append({
                'name': cells[1].get_text(strip=True),
                'price': cells[2].get_text(strip=True)
            })
    return stocks

# 2. 팝업 표시
def show_popup(code="KPI200"):
    stocks = get_top5(code)
    
    popup = tk.Tk()
    popup.title(f"📊 {code} - Top 5")
    
    ttk.Label(popup, text=f"🎯 {code} Top 5", font=("Arial", 14, "bold")).pack()
    
    for i, stock in enumerate(stocks, 1):
        ttk.Label(popup, text=f"{i}. {stock['name']} | ₩{stock['price']}").pack()
    
    ttk.Button(popup, text="닫기", command=popup.destroy).pack()
    popup.mainloop()

# 3. 실행
if __name__ == "__main__":
    show_popup("KPI200")
```

**설명:**
1. `requests.get()` - 네이버 금융 페이지 요청
2. `BeautifulSoup()` - HTML 파싱
3. `find_all('table')` - 모든 테이블 찾기
4. `[1:6]` - 2번째 테이블의 1~5행 추출
5. `tkinter` - GUI 팝업 표시

---

## 📊 지수 코드 참고

```
코드         지수명          설명
─────────────────────────────────────────────
KPI200      코스피200       KOSPI200 지수 (대형주)
KOSPI       코스피          전체 시장 지수
KOSDAQ      코스닥          기술주 중심 지수
KOSPI100    코스피100       KOSPI 상위 100개
KOSPI50     코스피50        대형주 50개
DJI         다우            미국 지수
IXIC        나스닥          미국 기술주 지수
```

---

## ✅ 체크리스트

### 설치 및 준비
- [ ] Python 3.6 이상 설치
- [ ] `pip install requests beautifulsoup4` 실행
- [ ] 파일 다운로드 확인

### 기본 실행
- [ ] `python stock_popup_gui.py` 실행 시 윈도우 열림
- [ ] 버튼 클릭하면 팝업 나타남
- [ ] Top 5 종목이 정상 표시됨

### 고급 기능
- [ ] 새로고침 버튼 동작 확인
- [ ] 여러 지수 크롤링 테스트
- [ ] CSV/JSON 저장 확인

---

## 🐛 문제 해결

### Q: ImportError: No module named 'requests'
**A:** 라이브러리 설치 필요
```bash
pip install requests beautifulsoup4
```

### Q: 한글이 깨짐
**A:** 파일 인코딩 확인
```python
response.encoding = 'utf-8'  # 필수
```

### Q: GUI 팝업이 안 열림
**A:** tkinter 설치
```bash
pip install tk  # 또는 콘솔 버전 사용
```

### Q: 데이터가 로드 안 됨
**A:** 네이버 서버 상태 확인
- 인터넷 연결 확인
- 방화벽 설정 확인
- 네이버 금융 페이지 직접 접속 테스트

### Q: 너무 느림
**A:** 
- 콘솔 버전 사용 (`stock_top5_console.py`)
- 인터넷 속도 확인
- 다른 작업 종료

---

## 🎓 학습 순서 추천

### Level 1️⃣: 초급 (기본 개념)
1. `naver_finance_simple.py` 읽기
2. 코드에서 `get_top5_stocks()` 함수 이해
3. BeautifulSoup 기본 문법 학습

### Level 2️⃣: 중급 (클래스 설계)
1. `naver_kospi200_complete.py` 읽기
2. 클래스 구조 이해
3. 메서드 작성 및 수정

### Level 3️⃣: 고급 (확장 기능)
1. `naver_stock_crawler.py` 읽기
2. CSV/JSON 저장 구현
3. 에러 처리 강화

### Level 4️⃣: 실무 (최적화)
1. 멀티스레딩 추가
2. 데이터베이스 연동
3. 웹 서비스 배포

---

## 💡 응용 아이디어

### 1️⃣ 데이터 시각화
```python
import matplotlib.pyplot as plt

# Top 5 종목을 그래프로 표시
```

### 2️⃣ 실시간 알림
```python
# 가격 변동 시 알림 설정
while True:
    current = get_top5()
    if current != previous:
        send_notification()
```

### 3️⃣ 웹 대시보드
```python
from flask import Flask
# Flask를 사용한 웹 서비스
```

### 4️⃣ 모바일 앱
```python
from kivy.app import App
# Kivy를 사용한 모바일 앱
```

### 5️⃣ 자동 매매
```python
# 크롤링 데이터 기반 자동 거래
```

---

## 📚 추가 학습 자료

### 공식 문서
- [BeautifulSoup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [requests 라이브러리](https://requests.readthedocs.io/)
- [tkinter 튜토리얼](https://docs.python.org/3/library/tkinter.html)

### 웹 크롤링
- [Web Scraping with Python](https://realpython.com/beautiful-soup-web-scraper-python/)
- [BeautifulSoup 한글 가이드](https://www.geeksforgeeks.org/beautifulsoup/)

### 금융 데이터
- [네이버 금융](https://finance.naver.com/)
- [한국거래소](https://www.krx.co.kr/)
- [금융감독원](https://www.fss.or.kr/)

---

## 🎉 완료!

축하합니다! 🎊

네이버 금융 Top 5 종목 팝업 시스템을 완성했습니다!

### 다음 단계:
1. ✅ 원하는 버전 선택하여 실행
2. ✅ 코드 분석 및 학습
3. ✅ 필요에 맞게 커스터마이징
4. ✅ 다른 프로젝트에 응용

---

**작성자**: AI Assistant  
**완성일**: 2025년 11월 13일  
**버전**: 1.0 Final  
**상태**: ✅ 완성 및 테스트 완료
