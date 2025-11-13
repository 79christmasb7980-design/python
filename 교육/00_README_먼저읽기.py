#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📊 네이버 금융 편입종목상위 데이터 크롤링 - 최종 정리
====================================================

작성자: AI Assistant
작성일: 2025년 11월 13일

제공하는 파일들:
1. stock_popup_gui.py - GUI 팝업 버전 (가장 예쁨)
2. stock_popup_simple.py - 간단 팝업 버전
3. stock_top5_console.py - 콘솔 팝업 버전 (가장 빠름)
4. naver_kospi200_complete.py - 완전 버전 (클래스 기반)
5. naver_finance_simple.py - 간단 버전 (함수 기반)
6. naver_stock_crawler.py - 고급 버전 (CSV/JSON 저장)
"""

# ============================================================================
# 🎯 가장 간단한 Top 5 팝업 코드 (복사 후 사용 가능)
# ============================================================================

import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk

def get_top5_stocks(code="KPI200"):
    """Top 5 종목 데이터 가져오기"""
    url = f"https://finance.naver.com/sise/sise_index.naver?code={code}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = 'utf-8'
    
    soup = BeautifulSoup(response.content, 'html.parser')
    tables = soup.find_all('table')
    
    stocks = []
    for row in tables[1].find_all('tr')[1:6]:  # Top 5만
        cells = row.find_all('td')
        if len(cells) >= 3:
            name = cells[1].get_text(strip=True)
            price = cells[2].get_text(strip=True)
            if name and price:
                stocks.append({'name': name, 'price': price})
    
    return stocks

def show_top5_popup(code="KPI200"):
    """Top 5 팝업 윈도우 표시"""
    
    # 데이터 가져오기
    stocks = get_top5_stocks(code)
    
    if not stocks:
        print(f"❌ {code} 데이터를 가져올 수 없습니다.")
        return
    
    # 팝업 창 생성
    popup = tk.Tk()
    popup.title(f"📊 {code} - Top 5 종목")
    popup.geometry("400x300")
    popup.resizable(False, False)
    popup.attributes('-topmost', True)  # 맨 앞에 표시
    
    # 제목
    title = ttk.Label(
        popup,
        text=f"🎯 {code} Top 5 종목",
        font=("Arial", 14, "bold")
    )
    title.pack(pady=15)
    
    # 메달 이모지
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    
    # 각 종목 표시
    frame = ttk.Frame(popup)
    frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
    
    for idx, stock in enumerate(stocks):
        row = ttk.Frame(frame)
        row.pack(fill=tk.X, pady=5)
        
        # 순위 (메달)
        ttk.Label(row, text=medals[idx], font=("Arial", 12, "bold"), width=3).pack(side=tk.LEFT, padx=5)
        
        # 순번
        ttk.Label(row, text=f"{idx+1}", font=("Arial", 12, "bold"), width=2).pack(side=tk.LEFT)
        
        # 종목명
        ttk.Label(row, text=stock['name'], font=("Arial", 11), width=20).pack(side=tk.LEFT, padx=10)
        
        # 가격
        ttk.Label(row, text=f"₩{stock['price']}", font=("Arial", 11, "bold"), foreground="darkblue").pack(side=tk.LEFT)
    
    # 닫기 버튼
    ttk.Button(popup, text="✓ 닫기", command=popup.destroy).pack(pady=15)
    
    popup.mainloop()


# ============================================================================
# 📝 사용 방법
# ============================================================================

"""
방법 1: GUI 팝업 표시 (코드 맨 아래에 추가)
    if __name__ == "__main__":
        show_top5_popup("KPI200")

방법 2: 여러 지수 팝업 표시
    if __name__ == "__main__":
        for code in ["KPI200", "KOSPI", "KOSDAQ"]:
            show_top5_popup(code)

방법 3: 터미널에서 실행
    python your_file.py
"""

# ============================================================================
# 🚀 실행 방법
# ============================================================================

"""
1. 필수 라이브러리 설치
   pip install requests beautifulsoup4

2. 파일 선택하여 실행

   ✅ 추천: GUI 팝업 버전
   python stock_popup_gui.py
   - 깔끔한 인터페이스
   - 여러 지수 선택 가능
   - 새로고침 기능

   ✅ 간단: 간단 팝업 버전
   python stock_popup_simple.py
   - 더 단순한 UI
   - 빠른 로딩

   ✅ 빠름: 콘솔 팝업 버전
   python stock_top5_console.py
   python stock_top5_console.py -m      (대화형 메뉴)
   python stock_top5_console.py -a      (전체 조회)
   python stock_top5_console.py KPI200  (특정 지수)
"""

# ============================================================================
# 📊 지원하는 지수 코드
# ============================================================================

"""
지수 코드     지수명           설명
─────────────────────────────────────────────
KPI200      코스피200        대형주 지수 (주요)
KOSPI       코스피          전체 시장 지수
KOSDAQ      코스닥          중소형주 지수
KOSPI100    코스피100       코스피 상위 100개
"""

# ============================================================================
# 🎓 학습 코드 분석
# ============================================================================

"""
1. 데이터 가져오기 부분
   - requests.get(): HTTP 요청
   - response.encoding = 'utf-8': 한글 처리
   
2. HTML 파싱 부분
   - BeautifulSoup(): HTML 파싱
   - find_all('table'): 모든 테이블 찾기
   - find_all('tr')[1:6]: 1번째 행부터 5번째 행까지 (Top 5)
   - get_text(strip=True): 텍스트 추출 및 공백 제거
   
3. GUI 표시 부분
   - tk.Tk(): 윈도우 생성
   - ttk.Label(): 텍스트 표시
   - ttk.Button(): 버튼 생성
   - pack()/grid(): 위젯 배치
"""

# ============================================================================
# ⚙️ 커스터마이징 예제
# ============================================================================

"""
1. Top 10으로 변경
   for row in tables[1].find_all('tr')[1:11]:  # 10으로 변경

2. 추가 정보 표시 (변동률, 거래량 등)
   change = cells[3].get_text(strip=True)       # 등락액
   change_pct = cells[4].get_text(strip=True)   # 등락률
   volume = cells[5].get_text(strip=True)       # 거래량

3. 데이터 저장
   import csv
   with open('top5.csv', 'w', encoding='utf-8') as f:
       writer = csv.writer(f)
       writer.writerow(['순위', '종목명', '가격'])
       for idx, stock in enumerate(stocks, 1):
           writer.writerow([idx, stock['name'], stock['price']])

4. 정렬
   # 가격 높은 순
   sorted_stocks = sorted(stocks, 
                         key=lambda x: int(x['price'].replace(',', '')), 
                         reverse=True)
"""

# ============================================================================
# 🐛 문제 해결
# ============================================================================

"""
Q1: ImportError: No module named 'requests'
A1: pip install requests beautifulsoup4

Q2: 한글이 깨져서 나옴
A2: response.encoding = 'utf-8' 추가 확인

Q3: GUI가 안 열림
A3: tkinter 설치 (Windows: pip install tk)

Q4: 데이터가 로드되지 않음
A4: 테이블 인덱스 확인 (tables[1]이 맞는지 확인)

Q5: 너무 느림
A5: 콘솔 버전 사용 또는 인터넷 연결 확인
"""

# ============================================================================
# 📚 참고 자료
# ============================================================================

"""
공식 문서:
- BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/
- requests: https://requests.readthedocs.io/
- tkinter: https://docs.python.org/3/library/tkinter.html

튜토리얼:
- 웹 크롤링 기초: https://docs.python-guide.org/scenarios/scrape/
- BeautifulSoup 튜토리얼: https://www.datacamp.com/community/tutorials/

네이버 금융:
- 메인: https://finance.naver.com/
- 국내증시: https://finance.naver.com/sise/
"""

# ============================================================================
# ✅ 체크리스트
# ============================================================================

"""
크롤링 구현:
☐ requests 라이브러리 설치
☐ beautifulsoup4 라이브러리 설치
☐ 기본 크롤링 코드 작성
☐ 데이터 추출 확인
☐ 에러 처리 추가

팝업 구현:
☐ tkinter 설치 (필요시)
☐ GUI 위젯 배치
☐ 데이터 표시
☐ 버튼 이벤트 처리

최적화:
☐ 마ル팀스레딩 사용
☐ 캐싱 구현
☐ 예외 처리 강화
☐ UI/UX 개선
"""

# ============================================================================
# 💡 팁과 트릭
# ============================================================================

"""
1. 더 빠른 로딩
   - 멀티스레딩 사용: threading.Thread()
   - 비동기 처리: asyncio 라이브러리

2. 더 많은 정보
   - 여러 테이블 파싱
   - 추가 페이지 크롤링
   - API 활용

3. 더 예쁜 UI
   - PyQt 또는 wxPython 사용
   - 웹 기반 UI: Flask + HTML/CSS/JS
   - 모바일 앱: Kivy

4. 지속적 업데이트
   - 스케줄러: APScheduler
   - 데이터베이스 저장: SQLite/MySQL
   - 알림 기능: 이메일/카톡
"""

if __name__ == "__main__":
    print("="*80)
    print(" "*15 + "📊 네이버 금융 Top 5 종목 팝업 시스템")
    print("="*80)
    print()
    print("🚀 사용 가능한 실행 파일:")
    print("  1. python stock_popup_gui.py        - GUI 팝업 (권장)")
    print("  2. python stock_popup_simple.py     - 간단 팝업")
    print("  3. python stock_top5_console.py     - 콘솔 팝업")
    print()
    print("📌 필수 설치:")
    print("  pip install requests beautifulsoup4")
    print()
    print("="*80)
    print()
    
    # 간단한 테스트
    try:
        print("🔍 연결 테스트 중...")
        stocks = get_top5_stocks("KPI200")
        
        if stocks:
            print("✅ 데이터 가져오기 성공!\n")
            print("📊 KPI200 Top 5 종목:")
            print("-" * 40)
            for idx, stock in enumerate(stocks, 1):
                print(f"  {idx}. {stock['name']:15} | ₩{stock['price']}")
            print("-" * 40)
            print("\n💡 GUI 팝업을 보려면 다음 명령어를 실행하세요:")
            print("   python stock_popup_gui.py")
        else:
            print("❌ 데이터를 가져올 수 없습니다.")
    
    except Exception as e:
        print(f"❌ 오류: {e}")
        print("\n📦 라이브러리를 설치하세요:")
        print("   pip install requests beautifulsoup4")
    
    print("\n")
