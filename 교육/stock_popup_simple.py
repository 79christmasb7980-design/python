"""
네이버 금융 편입종목상위 - 간단 팝업 버전
=========================================

한 번의 클릭으로 팝업에서 Top 5 종목을 확인합니다.
(tkinter 사용)
"""

import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox, ttk
import threading


def get_top_stocks(code="KPI200", limit=5):
    """Top N 종목 데이터 가져오기"""
    try:
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
                # 링크가 있으면 링크 텍스트만 추출
                name_cell = cells[1]
                link = name_cell.find('a')
                stock_name = link.get_text(strip=True) if link else name_cell.get_text(strip=True)
                
                stock_price = cells[2].get_text(strip=True)
                
                if stock_name and stock_price and len(stock_name) > 1:
                    stocks.append({'name': stock_name, 'price': stock_price})
        
        return stocks
    
    except Exception as e:
        print(f"에러: {e}")
        return None


def show_popup(code="KPI200"):
    """팝업 윈도우 표시"""
    
    # 팝업 창 생성
    popup = tk.Tk()
    popup.title(f"📊 {code} - Top 5 종목")
    popup.geometry("450x350")
    popup.resizable(False, False)
    popup.attributes('-topmost', True)
    
    # 로딩 상태
    loading_label = ttk.Label(popup, text="⏳ 데이터 로딩 중...", font=("Arial", 12))
    loading_label.pack(pady=20)
    
    def load_data():
        """데이터 로드 함수"""
        stocks = get_top_stocks(code, 5)
        
        # 로딩 메시지 제거
        loading_label.pack_forget()
        
        if not stocks:
            error_label = ttk.Label(popup, text="❌ 데이터를 가져올 수 없습니다.", font=("Arial", 11))
            error_label.pack(pady=20)
            return
        
        # 제목 프레임
        title_frame = ttk.Frame(popup)
        title_frame.pack(fill=tk.X, padx=20, pady=15)
        
        title_label = ttk.Label(
            title_frame,
            text=f"🎯 {code} 상위 5개 종목",
            font=("Arial", 13, "bold")
        )
        title_label.pack()
        
        # 테이블 프레임
        table_frame = ttk.Frame(popup)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # 헤더
        header_frame = ttk.Frame(table_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="순위", font=("Arial", 10, "bold"), width=5).pack(side=tk.LEFT, padx=5)
        ttk.Label(header_frame, text="종목명", font=("Arial", 10, "bold"), width=20).pack(side=tk.LEFT, padx=5)
        ttk.Label(header_frame, text="가격", font=("Arial", 10, "bold"), width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(table_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 10))
        
        # 데이터 행
        for idx, stock in enumerate(stocks, 1):
            row_frame = ttk.Frame(table_frame)
            row_frame.pack(fill=tk.X, pady=8)
            
            # 순위 (색상 구분)
            rank_colors = {1: '#FFD700', 2: '#C0C0C0', 3: '#CD7F32'}
            rank_bg = rank_colors.get(idx, 'white')
            
            rank_label = tk.Label(
                row_frame,
                text=f"{idx}",
                font=("Arial", 11, "bold"),
                width=5,
                bg=rank_bg,
                relief=tk.RAISED
            )
            rank_label.pack(side=tk.LEFT, padx=5)
            
            # 종목명
            name_label = ttk.Label(
                row_frame,
                text=stock['name'],
                font=("Arial", 11),
                width=20
            )
            name_label.pack(side=tk.LEFT, padx=5)
            
            # 가격
            price_label = ttk.Label(
                row_frame,
                text=f"₩{stock['price']}",
                font=("Arial", 11, "bold"),
                width=15,
                foreground="darkblue"
            )
            price_label.pack(side=tk.LEFT, padx=5)
        
        # 하단 버튼
        button_frame = ttk.Frame(popup)
        button_frame.pack(fill=tk.X, padx=15, pady=15)
        
        ttk.Button(button_frame, text="✓ 닫기", command=popup.destroy).pack()
    
    # 백그라운드에서 데이터 로드
    thread = threading.Thread(target=load_data, daemon=True)
    thread.start()
    
    popup.mainloop()


def create_main_window():
    """메인 윈도우 생성"""
    
    root = tk.Tk()
    root.title("📈 네이버 금융 Top 5 조회")
    root.geometry("450x400")
    
    # 메인 프레임
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 제목
    title = ttk.Label(
        main_frame,
        text="🎯 네이버 금융 Top 5 종목",
        font=("Arial", 16, "bold")
    )
    title.pack(pady=20)
    
    # 설명
    desc = ttk.Label(
        main_frame,
        text="팝업으로 상위 5개 종목을 확인하세요.",
        font=("Arial", 11),
        foreground="gray"
    )
    desc.pack(pady=10)
    
    # 구분선
    ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
    
    # 버튼들
    button_frame = ttk.LabelFrame(main_frame, text="📊 지수 선택", padding="15")
    button_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    indices = [
        ("📍 코스피200 (KPI200)", "KPI200"),
        ("📍 코스피 (KOSPI)", "KOSPI"),
        ("📍 코스닥 (KOSDAQ)", "KOSDAQ"),
        ("📍 코스피100 (KOSPI100)", "KOSPI100"),
    ]
    
    for label, code in indices:
        btn = ttk.Button(
            button_frame,
            text=label,
            command=lambda c=code: show_popup(c)
        )
        btn.pack(fill=tk.X, pady=10)
    
    # 구분선
    ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
    
    # 정보
    info_frame = ttk.LabelFrame(main_frame, text="ℹ️  정보", padding="10")
    info_frame.pack(fill=tk.X)
    
    info_text = ttk.Label(
        info_frame,
        text="• 실시간 데이터를 크롤링합니다.\n"
             "• 각 버튼을 클릭하면 팝업이 열립니다.\n"
             "• 상위 5개 종목을 확인할 수 있습니다.",
        font=("Arial", 9),
        justify=tk.LEFT
    )
    info_text.pack(anchor=tk.W)
    
    root.mainloop()


if __name__ == "__main__":
    print("🚀 네이버 금융 Top 5 조회 프로그램 시작...\n")
    create_main_window()
