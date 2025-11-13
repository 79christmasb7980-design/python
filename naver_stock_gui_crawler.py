import sys
import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QSpinBox, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor


class CrawlerThread(QThread):
    """크롤링을 별도 스레드에서 실행"""
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def run(self):
        try:
            # 네이버 파이낸스 KPI200 페이지 크롤링
            url = "https://finance.naver.com/sise/sise_index.naver?code=KPI200"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            html = response.text

            soup = BeautifulSoup(html, 'html.parser')

            # 대상 주식: 하이닉스, 유라클, 이마트
            target_stocks = ['하이닉스', '유라클', '이마트']
            stock_data = []

            # 테이블에서 주식 정보 추출
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) > 0:
                        # 첫 번째 컬럼에서 주식명 추출
                        stock_name_elem = cols[0].find('a')
                        if stock_name_elem:
                            stock_name = stock_name_elem.get_text(strip=True)
                            
                            # 대상 주식인지 확인
                            if any(target in stock_name for target in target_stocks):
                                # 각 컬럼 데이터 추출
                                try:
                                    price = cols[1].get_text(strip=True) if len(cols) > 1 else '-'
                                    change = cols[2].get_text(strip=True) if len(cols) > 2 else '-'
                                    change_rate = cols[3].get_text(strip=True) if len(cols) > 3 else '-'
                                    volume = cols[4].get_text(strip=True) if len(cols) > 4 else '-'

                                    stock_data.append({
                                        'name': stock_name,
                                        'price': price,
                                        'change': change,
                                        'change_rate': change_rate,
                                        'volume': volume
                                    })
                                except Exception as e:
                                    print(f"데이터 추출 오류: {e}")

            if not stock_data:
                # 대체 방식으로 크롤링
                stock_data = self.crawl_alternative_method(url, headers, target_stocks)

            self.finished.emit(stock_data)

        except Exception as e:
            self.error.emit(f"크롤링 오류: {str(e)}")

    def crawl_alternative_method(self, url, headers, target_stocks):
        """대체 크롤링 방식"""
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            html = response.text

            soup = BeautifulSoup(html, 'html.parser')
            stock_data = []

            # 모든 텍스트에서 대상 주식 검색
            all_text = soup.get_text()
            
            # 테이블 행 단위로 파싱
            for table in soup.find_all('table'):
                for row in table.find_all('tr'):
                    row_text = row.get_text()
                    
                    for target in target_stocks:
                        if target in row_text:
                            # 해당 행의 모든 셀 데이터 추출
                            cells = row.find_all('td')
                            if len(cells) >= 5:
                                stock_data.append({
                                    'name': target,
                                    'price': cells[1].get_text(strip=True) if len(cells) > 1 else '-',
                                    'change': cells[2].get_text(strip=True) if len(cells) > 2 else '-',
                                    'change_rate': cells[3].get_text(strip=True) if len(cells) > 3 else '-',
                                    'volume': cells[4].get_text(strip=True) if len(cells) > 4 else '-'
                                })

            return stock_data
        except Exception as e:
            raise Exception(f"대체 크롤링 실패: {str(e)}")


class StockCrawlerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.crawler_thread = None
        self.init_ui()

    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle('네이버 주식 크롤링 프로그램 - KPI200')
        self.setGeometry(100, 100, 900, 500)

        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 레이아웃
        main_layout = QVBoxLayout()

        # 제목
        title_label = QLabel('네이버 파이낸스 - KPI200 주식 정보 크롤링')
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)

        # 설명
        description_label = QLabel('대상 주식: 하이닉스, 유라클, 이마트')
        main_layout.addWidget(description_label)

        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        
        self.crawl_button = QPushButton('크롤링 시작')
        self.crawl_button.clicked.connect(self.start_crawling)
        button_layout.addWidget(self.crawl_button)

        self.refresh_button = QPushButton('새로고침')
        self.refresh_button.clicked.connect(self.start_crawling)
        button_layout.addWidget(self.refresh_button)

        main_layout.addLayout(button_layout)

        # 테이블 위젯
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(['주식명', '현재가', '변동가', '변동률(%)', '거래량'])
        self.table_widget.resizeColumnsToContents()
        main_layout.addWidget(self.table_widget)

        # 상태 레이블
        self.status_label = QLabel('준비 중...')
        main_layout.addWidget(self.status_label)

        central_widget.setLayout(main_layout)

    def start_crawling(self):
        """크롤링 시작"""
        self.crawl_button.setEnabled(False)
        self.refresh_button.setEnabled(False)
        self.status_label.setText('크롤링 중...')
        
        self.crawler_thread = CrawlerThread()
        self.crawler_thread.finished.connect(self.on_crawling_finished)
        self.crawler_thread.error.connect(self.on_crawling_error)
        self.crawler_thread.start()

    def on_crawling_finished(self, stock_data):
        """크롤링 완료"""
        self.table_widget.setRowCount(len(stock_data))

        for row, stock in enumerate(stock_data):
            # 주식명
            name_item = QTableWidgetItem(stock['name'])
            self.table_widget.setItem(row, 0, name_item)

            # 현재가
            price_item = QTableWidgetItem(stock['price'])
            self.table_widget.setItem(row, 1, price_item)

            # 변동가
            change_item = QTableWidgetItem(stock['change'])
            change_value = stock['change'].replace(',', '')
            try:
                if float(change_value) > 0:
                    change_item.setBackground(QColor(255, 100, 100))  # 빨강
                elif float(change_value) < 0:
                    change_item.setBackground(QColor(100, 100, 255))  # 파랑
            except:
                pass
            self.table_widget.setItem(row, 2, change_item)

            # 변동률
            rate_item = QTableWidgetItem(stock['change_rate'])
            self.table_widget.setItem(row, 3, rate_item)

            # 거래량
            volume_item = QTableWidgetItem(stock['volume'])
            self.table_widget.setItem(row, 4, volume_item)

        self.table_widget.resizeColumnsToContents()
        self.status_label.setText(f'크롤링 완료! ({len(stock_data)}개 항목)')
        self.crawl_button.setEnabled(True)
        self.refresh_button.setEnabled(True)

    def on_crawling_error(self, error_message):
        """크롤링 오류"""
        QMessageBox.critical(self, '오류', error_message)
        self.status_label.setText('크롤링 실패')
        self.crawl_button.setEnabled(True)
        self.refresh_button.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StockCrawlerGUI()
    window.show()
    sys.exit(app.exec_())
