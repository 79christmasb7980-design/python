"""
네이버 금융 편입종목상위 - Top 5 표시 (콘솔 버전)
==============================================

BeautifulSoup으로 크롤링하여 Top 5 종목을 정렬된 형식으로 표시합니다.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os


def clear_screen():
    """화면 초기화"""
    os.system('cls' if os.name == 'nt' else 'clear')


def get_top_stocks(code="KPI200", limit=5):
    """Top N 종목 크롤링"""
    try:
        print(f"\n⏳ {code} 데이터 로딩 중...")
        
        url = f"https://finance.naver.com/sise/sise_index.naver?code={code}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        # response.text로 자동 인코딩 감지
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')
        
        if len(tables) < 2:
            return None
        
        stocks = []
        rows = tables[1].find_all('tr')
        
        for row in rows[1:limit+1]:
            cells = row.find_all('td')
            if len(cells) >= 3:
                # 링크가 있으면 링크 텍스트 추출
                name_cell = cells[1]
                link = name_cell.find('a')
                stock_name = link.get_text(strip=True) if link else name_cell.get_text(strip=True)
                
                stock_price = cells[2].get_text(strip=True)
                
                if stock_name and stock_price and len(stock_name) > 1:
                    stocks.append({
                        'name': stock_name,
                        'price': stock_price
                    })
        
        return stocks
    
    except Exception as e:
        print(f"❌ 오류: {e}")
        return None


def display_top_5_popup(code="KPI200"):
    """Top 5 종목을 팝업 형식으로 표시"""
    
    stocks = get_top_stocks(code, 5)
    
    if not stocks:
        print(f"❌ {code} 데이터를 가져올 수 없습니다.")
        return
    
    # 팝업 상자 그리기
    print("\n")
    print("┌" + "─" * 60 + "┐")
    print("│" + f" 📊 {code} - Top 5 종목".center(60) + "│")
    print("├" + "─" * 60 + "┤")
    print("│" + " 순위 | 종목명           | 가격              ".ljust(60) + "│")
    print("├" + "─" * 60 + "┤")
    
    # 메달 이모지
    medals = ["🥇", "🥈", "🥉", "4️⃣ ", "5️⃣ "]
    
    for idx, stock in enumerate(stocks, 1):
        medal = medals[idx-1]
        name = stock['name'][:15].ljust(15)
        price = f"₩{stock['price']}".rjust(15)
        
        line = f"│ {medal} {idx} | {name} | {price}  │"
        print(line)
    
    print("└" + "─" * 60 + "┘")
    print(f"\n📅 조회 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def display_multiple_indices():
    """여러 지수의 Top 5를 표시"""
    
    clear_screen()
    
    print("="*80)
    print(" " * 20 + "🎯 네이버 금융 Top 5 종목 조회")
    print("="*80)
    
    indices = [
        ("코스피200", "KPI200"),
        ("코스피", "KOSPI"),
        ("코스닥", "KOSDAQ"),
    ]
    
    for label, code in indices:
        print(f"\n\n🔍 {label} 조회 중...")
        display_top_5_popup(code)
    
    print("\n\n" + "="*80)
    print("✅ 모든 조회가 완료되었습니다.")
    print("="*80 + "\n")


def interactive_menu():
    """대화형 메뉴"""
    
    while True:
        clear_screen()
        
        print("="*80)
        print(" " * 20 + "🎯 네이버 금융 Top 5 종목 조회")
        print("="*80)
        print("\n📊 조회할 지수를 선택하세요:\n")
        
        options = [
            ("1", "코스피200 (KPI200)", "KPI200"),
            ("2", "코스피 (KOSPI)", "KOSPI"),
            ("3", "코스닥 (KOSDAQ)", "KOSDAQ"),
            ("4", "코스피100 (KOSPI100)", "KOSPI100"),
            ("5", "전체 조회", None),
            ("0", "종료", None),
        ]
        
        for num, label, code in options:
            print(f"  {num}. {label}")
        
        choice = input("\n선택 (0-5): ").strip()
        
        if choice == "0":
            print("\n👋 프로그램을 종료합니다.\n")
            break
        elif choice == "5":
            display_multiple_indices()
            input("\n\n아무 키나 누르세요...")
        elif choice in ["1", "2", "3", "4"]:
            code_map = {"1": "KPI200", "2": "KOSPI", "3": "KOSDAQ", "4": "KOSPI100"}
            code = code_map[choice]
            
            clear_screen()
            display_top_5_popup(code)
            input("\n\n아무 키나 누르세요...")
        else:
            print("❌ 잘못된 선택입니다.")
            input("아무 키나 누르세요...")


def simple_display():
    """간단 표시 버전"""
    
    print("\n" + "="*80)
    print("🎯 네이버 금융 Top 5 종목 조회".center(80))
    print("="*80 + "\n")
    
    codes = ["KPI200", "KOSPI", "KOSDAQ"]
    
    for code in codes:
        display_top_5_popup(code)
        print()


if __name__ == "__main__":
    import sys
    
    # 명령행 인자 확인
    if len(sys.argv) > 1:
        if sys.argv[1] == "-m":
            # 대화형 메뉴 모드
            interactive_menu()
        elif sys.argv[1] == "-a":
            # 전체 조회 모드
            display_multiple_indices()
        else:
            # 특정 지수 조회
            code = sys.argv[1].upper()
            clear_screen()
            display_top_5_popup(code)
    else:
        # 기본 모드: 간단 표시
        simple_display()
    
    print()
