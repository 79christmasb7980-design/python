# 📊 네이버 금융 Top 5 종목 팝업 - 완전 가이드

네이버 금융에서 BeautifulSoup으로 크롤링한 **Top 5 종목**을 팝업으로 보여주는 세 가지 방법입니다.

---

## 🚀 빠른 시작

### 1️⃣ GUI 팝업 버전 (가장 예쁨)
```bash
python stock_popup_gui.py
```
✨ **특징:**
- 깔끔한 GUI 인터페이스
- 지수 선택 버튼
- 테이블 형식의 Top 5 종목 표시
- 새로고침 기능
- 다중 팝업 지원

### 2️⃣ 간단한 팝업 버전
```bash
python stock_popup_simple.py
```
✨ **특징:**
- 더 단순한 UI
- 빠른 로딩
- 기본 정보만 표시
- 부산스럽지 않음

### 3️⃣ 콘솔 팝업 버전 (가장 빠름)
```bash
python stock_top5_console.py          # 기본: 간단 표시
python stock_top5_console.py -m      # 대화형 메뉴
python stock_top5_console.py -a      # 전체 지수 조회
python stock_top5_console.py KPI200  # 특정 지수 조회
```
✨ **특징:**
- 터미널에서만 실행
- 가장 가벼움
- 빠른 실행 속도
- 아스키 아트 표현

---

## 📋 코드 비교

### GUI 팝업 버전 (권장)
```python
import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk
import threading

def get_top_stocks(code="KPI200", limit=5):
    """Top N 종목 데이터 가져오기"""
    url = f"https://finance.naver.com/sise/sise_index.naver?code={code}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = 'utf-8'
    
    soup = BeautifulSoup(response.content, 'html.parser')
    tables = soup.find_all('table')
    
    stocks = []
    rows = tables[1].find_all('tr')
    
    for row in rows[1:limit+1]:
        cells = row.find_all('td')
        if len(cells) >= 3:
            name = cells[1].get_text(strip=True)
            price = cells[2].get_text(strip=True)
            if name and price:
                stocks.append({'name': name, 'price': price})
    
    return stocks

def show_popup(code="KPI200"):
    """팝업 윈도우 표시"""
    popup = tk.Tk()
    popup.title(f"📊 {code} - Top 5 종목")
    popup.geometry("450x350")
    
    stocks = get_top_stocks(code, 5)
    
    # 제목
    title = ttk.Label(popup, text=f"🎯 {code} 상위 5개 종목", font=("Arial", 13, "bold"))
    title.pack(pady=15)
    
    # 데이터 표시
    for idx, stock in enumerate(stocks, 1):
        row_frame = ttk.Frame(popup)
        row_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(row_frame, text=f"{idx}.", font=("Arial", 11, "bold"), width=3).pack(side=tk.LEFT)
        ttk.Label(row_frame, text=stock['name'], font=("Arial", 11), width=20).pack(side=tk.LEFT, padx=10)
        ttk.Label(row_frame, text=f"₩{stock['price']}", font=("Arial", 11, "bold")).pack(side=tk.LEFT)
    
    ttk.Button(popup, text="닫기", command=popup.destroy).pack(pady=15)
    popup.mainloop()

if __name__ == "__main__":
    show_popup("KPI200")
```

### 콘솔 팝업 버전
```python
import requests
from bs4 import BeautifulSoup

def get_top_stocks(code="KPI200"):
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
            name = cells[1].get_text(strip=True)
            price = cells[2].get_text(strip=True)
            if name and price:
                stocks.append({'name': name, 'price': price})
    
    return stocks

def show_popup(code="KPI200"):
    stocks = get_top_stocks(code)
    
    print("\n" + "┌" + "─" * 60 + "┐")
    print("│" + f" 📊 {code} - Top 5 종목".center(60) + "│")
    print("├" + "─" * 60 + "┤")
    
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    
    for idx, stock in enumerate(stocks, 1):
        name = stock['name'][:15].ljust(15)
        price = f"₩{stock['price']}".rjust(15)
        print(f"│ {medals[idx-1]} {idx} | {name} | {price}  │")
    
    print("└" + "─" * 60 + "┘\n")

if __name__ == "__main__":
    show_popup("KPI200")
```

---

## 🎯 사용 방법

### GUI 메인 윈도우에서 사용
1. `stock_popup_gui.py` 실행
2. 버튼 클릭하여 지수 선택
3. 팝업 윈도우에서 Top 5 종목 확인
4. "새로고침" 클릭으로 최신 데이터 로드

### 콘솔에서 사용
```bash
# 대화형 메뉴 모드
python stock_top5_console.py -m

# 전체 지수 조회
python stock_top5_console.py -a

# 특정 지수만 조회
python stock_top5_console.py KPI200
```

---

## 📊 지원하는 지수 코드

| 코드 | 지수명 | 설명 |
|------|--------|------|
| KPI200 | 코스피200 | 대형주 지수 |
| KOSPI | 코스피 | 전체 시장 지수 |
| KOSDAQ | 코스닥 | 중소형주 지수 |
| KOSPI100 | 코스피100 | 코스피 상위 100개 |

---

## 🔧 커스터마이징

### Top 5를 Top 10으로 변경
```python
stocks = get_top_stocks(code, 10)  # 10으로 변경
```

### 다른 정보 표시
```python
# 거래량, 등락률 등도 추출 가능
for row in tables[1].find_all('tr')[1:6]:
    cells = row.find_all('td')
    name = cells[1].get_text(strip=True)        # 종목명
    price = cells[2].get_text(strip=True)       # 가격
    change = cells[3].get_text(strip=True)      # 등락액
    change_pct = cells[4].get_text(strip=True)  # 등락률
    volume = cells[5].get_text(strip=True)      # 거래량
```

### 색상 커스터마이징 (GUI)
```python
rank_colors = {
    1: '#FFD700',  # 금색
    2: '#C0C0C0',  # 은색
    3: '#CD7F32'   # 동색
}
```

---

## ⚠️ 주의사항

### 1. User-Agent 필수
네이버는 봇 차단을 위해 User-Agent를 검증합니다:
```python
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...'}
```

### 2. 인코딩 설정
한글 데이터를 올바르게 처리하려면:
```python
response.encoding = 'utf-8'
```

### 3. 요청 지연
서버 부하 방지를 위해 요청 간 지연 추가:
```python
import time
time.sleep(1)  # 1초 대기
```

### 4. 에러 처리
네트워크 오류에 대비:
```python
try:
    response = requests.get(url, headers=headers, timeout=10)
except Exception as e:
    print(f"❌ 오류: {e}")
```

---

## 🐛 문제 해결

### Q: "ModuleNotFoundError: No module named 'requests'"
**해결책:**
```bash
pip install requests beautifulsoup4
```

### Q: 한글이 깨져서 나옴
**해결책:**
```python
response.encoding = 'utf-8'
```

### Q: 팝업이 열리지 않음
**해결책:**
```bash
# tkinter 설치 (Windows)
pip install tk

# 또는 콘솔 버전 사용
python stock_top5_console.py
```

### Q: 데이터가 너무 느림
**해결책:**
- 콘솔 버전 사용 (더 빠름)
- 인터넷 연결 확인
- 네이버 서버 상태 확인

---

## 📈 결과 예시

```
┌────────────────────────────────────────────────────────────┐
│                  📊 KPI200 - Top 5 종목                     │
├────────────────────────────────────────────────────────────┤
│ 순위 | 종목명           | 가격                              │
├────────────────────────────────────────────────────────────┤
│ 🥇 1 | SK하이닉스       | ₩616,000  │
│ 🥈 2 | 에이비엘바이오   | ₩161,900  │
│ 🥉 3 | 두산에너빌리티   | ₩80,500   │
│ 4️⃣  4 | 한화오션        | ₩125,200  │
│ 5️⃣  5 | (다섯 번째)     | ₩000,000  │
└────────────────────────────────────────────────────────────┘

📅 조회 시간: 2025-11-13 10:14:37
```

---

## 🎓 학습 포인트

✅ **BeautifulSoup 사용법**
- HTML 파싱
- CSS 선택자
- 데이터 추출

✅ **requests 라이브러리**
- HTTP 요청
- 헤더 설정
- 인코딩 처리

✅ **tkinter GUI**
- 윈도우 생성
- 위젯 배치
- 이벤트 처리

✅ **데이터 처리**
- 리스트 조작
- 문자열 포맷팅
- 예외 처리

---

## 📚 참고 자료

- [BeautifulSoup 공식 문서](https://www.crummy.com/software/BeautifulSoup/)
- [requests 공식 문서](https://requests.readthedocs.io/)
- [tkinter 공식 튜토리얼](https://docs.python.org/3/library/tkinter.html)
- [네이버 금융](https://finance.naver.com/)

---

## ✅ 체크리스트

- [ ] `requests` 라이브러리 설치
- [ ] `beautifulsoup4` 라이브러리 설치
- [ ] 세 가지 버전 중 선호하는 것 선택
- [ ] 코드 실행 확인
- [ ] Top 5 데이터 정상 표시 확인
- [ ] 여러 지수 코드 테스트

---

**작성자**: AI Assistant  
**작성일**: 2025년 11월 13일  
**마지막 수정**: 2025년 11월 13일  
**버전**: 1.0
