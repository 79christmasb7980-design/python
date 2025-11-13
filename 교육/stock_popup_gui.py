"""
네이버 금융 편입종목상위 - 팝업 표시 버전
========================================

tkinter를 사용하여 상위 5개 종목을 팝업 윈도우에 표시합니다.
"""

import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading


class StockPopupCrawler:
    """팝업으로 종목 정보를 표시하는 크롤러"""
    
    def __init__(self):
        self.base_url = "https://finance.naver.com/sise/sise_index.naver"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_top_stocks(self, code="KPI200", limit=5):
        """상위 N개 종목 데이터 가져오기"""
        try:
            print(f"📡 {code} 크롤링 중...")
            
            url = f"{self.base_url}?code={code}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            # 응답 텍스트로 BeautifulSoup 파싱 (자동 인코딩 감지)
            soup = BeautifulSoup(response.text, 'html.parser')
            tables = soup.find_all('table')
            
            if len(tables) < 2:
                return None
            
            # 두 번째 테이블에서 종목 데이터 추출 (상위 N개)
            table = tables[1]
            rows = table.find_all('tr')
            
            stocks = []
            for row in rows[1:limit+1]:  # 상위 N개만
                cells = row.find_all('td')
                if len(cells) >= 3:
                    # 링크 태그가 있으면 텍스트만 추출, 없으면 직접 추출
                    name_cell = cells[1]
                    link = name_cell.find('a')
                    stock_name = link.get_text(strip=True) if link else name_cell.get_text(strip=True)
                    
                    stock_price = cells[2].get_text(strip=True)
                    
                    # 유효한 데이터만 추가 (중국어 등 깨진 텍스트 제외)
                    if stock_name and stock_price and len(stock_name) > 1:
                        stocks.append({
                            'name': stock_name,
                            'price': stock_price
                        })
            
            return stocks
        
        except Exception as e:
            print(f"❌ 크롤링 에러: {e}")
            import traceback
            traceback.print_exc()
            return None


class StockPopupUI:
    """팝업 UI를 관리하는 클래스"""
    
    def __init__(self, root):
        self.root = root
        self.crawler = StockPopupCrawler()
    
    def show_popup(self, code="KPI200", limit=5):
        """팝업 창 표시"""
        
        # 백그라운드에서 크롤링 수행
        def fetch_and_display():
            stocks = self.crawler.fetch_top_stocks(code, limit)
            
            if not stocks:
                messagebox.showerror("오류", f"{code} 데이터를 가져올 수 없습니다.")
                return
            
            # 팝업 창 생성
            popup = tk.Toplevel(self.root)
            popup.title(f"📊 {code} - Top {limit} 종목")
            popup.geometry("400x300")
            popup.resizable(False, False)
            
            # 중앙에 배치
            popup.attributes('-topmost', True)  # 맨 앞에 표시
            
            # 제목
            title_frame = ttk.Frame(popup)
            title_frame.pack(fill=tk.X, padx=20, pady=15)
            
            title_label = ttk.Label(
                title_frame,
                text=f"🎯 {code} 상위 {limit}개 종목",
                font=("Arial", 14, "bold")
            )
            title_label.pack()
            
            # 트리뷰 (테이블)
            tree_frame = ttk.Frame(popup)
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
            
            # 스크롤바
            scrollbar = ttk.Scrollbar(tree_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # 트리뷰
            tree = ttk.Treeview(
                tree_frame,
                columns=("순위", "종목명", "가격"),
                height=10,
                show="headings",
                yscrollcommand=scrollbar.set
            )
            scrollbar.config(command=tree.yview)
            
            # 컬럼 설정
            tree.column("#0", width=0, stretch=tk.NO)
            tree.column("순위", anchor=tk.CENTER, width=40)
            tree.column("종목명", anchor=tk.W, width=150)
            tree.column("가격", anchor=tk.E, width=100)
            
            tree.heading("#0", text="")
            tree.heading("순위", text="순위")
            tree.heading("종목명", text="종목명")
            tree.heading("가격", text="가격")
            
            # 데이터 입력
            for idx, stock in enumerate(stocks, 1):
                tree.insert(
                    "",
                    "end",
                    values=(
                        f"{idx}",
                        stock['name'],
                        stock['price']
                    )
                )
            
            # 짝/홀 행 색상 구분
            tree.tag_configure('oddrow', background='#f0f0f0')
            tree.tag_configure('evenrow', background='white')
            
            for idx, item in enumerate(tree.get_children()):
                if idx % 2 == 0:
                    tree.item(item, tags=('evenrow',))
                else:
                    tree.item(item, tags=('oddrow',))
            
            tree.pack(fill=tk.BOTH, expand=True)
            
            # 버튼 프레임
            button_frame = ttk.Frame(popup)
            button_frame.pack(fill=tk.X, padx=15, pady=10)
            
            # 새로고침 버튼
            refresh_btn = ttk.Button(
                button_frame,
                text="🔄 새로고침",
                command=lambda: self.refresh_stocks(popup, tree, code, limit)
            )
            refresh_btn.pack(side=tk.LEFT, padx=5)
            
            # 닫기 버튼
            close_btn = ttk.Button(
                button_frame,
                text="❌ 닫기",
                command=popup.destroy
            )
            close_btn.pack(side=tk.RIGHT, padx=5)
        
        # 스레드에서 크롤링 실행
        thread = threading.Thread(target=fetch_and_display, daemon=True)
        thread.start()
    
    def refresh_stocks(self, popup, tree, code, limit):
        """종목 정보 새로고침"""
        
        # 기존 데이터 삭제
        for item in tree.get_children():
            tree.delete(item)
        
        # 새 데이터 로드
        stocks = self.crawler.fetch_top_stocks(code, limit)
        
        if stocks:
            for idx, stock in enumerate(stocks, 1):
                tree.insert(
                    "",
                    "end",
                    values=(
                        f"{idx}",
                        stock['name'],
                        stock['price']
                    )
                )
            
            messagebox.showinfo("성공", "데이터를 새로고침했습니다.")
        else:
            messagebox.showerror("오류", "데이터를 다시 가져올 수 없습니다.")


class MainWindow:
    """메인 윈도우"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("📈 네이버 금융 크롤러")
        self.root.geometry("500x350")
        
        self.popup_ui = StockPopupUI(root)
        
        self.setup_ui()
    
    def setup_ui(self):
        """UI 설정"""
        
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 제목
        title_label = ttk.Label(
            main_frame,
            text="🎯 네이버 금융 Top 5 종목 조회",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=20)
        
        # 설명
        desc_label = ttk.Label(
            main_frame,
            text="아래 버튼을 클릭하여 팝업으로 상위 5개 종목을 확인하세요.",
            font=("Arial", 10),
            foreground="gray"
        )
        desc_label.pack(pady=10)
        
        # 구분선
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # 버튼들
        button_frame = ttk.LabelFrame(main_frame, text="지수 선택", padding="15")
        button_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        indices = [
            ("코스피200 (KPI200)", "KPI200"),
            ("코스피 (KOSPI)", "KOSPI"),
            ("코스닥 (KOSDAQ)", "KOSDAQ"),
            ("코스피100 (KOSPI100)", "KOSPI100"),
        ]
        
        for label, code in indices:
            btn = ttk.Button(
                button_frame,
                text=f"📊 {label}",
                command=lambda c=code: self.popup_ui.show_popup(c, 5)
            )
            btn.pack(fill=tk.X, pady=8)
        
        # 구분선
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # 정보 패널
        info_frame = ttk.LabelFrame(main_frame, text="정보", padding="10")
        info_frame.pack(fill=tk.X)
        
        info_text = ttk.Label(
            info_frame,
            text="• BeautifulSoup을 사용하여 실시간 데이터를 크롤링합니다.\n"
                 "• 팝업 창에서 상위 5개 종목을 확인할 수 있습니다.\n"
                 "• '새로고침' 버튼으로 최신 데이터를 다시 로드할 수 있습니다.",
            font=("Arial", 9),
            justify=tk.LEFT
        )
        info_text.pack(anchor=tk.W)


def main():
    """메인 함수"""
    
    root = tk.Tk()
    
    # 윈도우 아이콘 설정 (옵션)
    try:
        root.iconbitmap(default='')  # 기본 아이콘 사용
    except:
        pass
    
    # 윈도우 스타일 설정
    style = ttk.Style()
    style.theme_use('clam')  # 또는 'alt', 'default'
    
    app = MainWindow(root)
    
    root.mainloop()


if __name__ == "__main__":
    print("🚀 네이버 금융 크롤러 시작...")
    print("ℹ️  메인 윈도우가 열렸습니다.\n")
    main()
