#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
KIMPGA 암호화폐 크롤러 - 간단한 PyQt5 GUI 버전
더 간편한 인터페이스로 기본 기능만 제공
"""

import sys
import os
import json
import csv
from datetime import datetime
from pathlib import Path

# sys.path 정리
if 'c:\\work' in sys.path:
    sys.path.remove('c:\\work')
work_path = os.path.dirname(os.path.abspath(__file__))
if work_path in sys.path:
    sys.path.remove(work_path)

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QProgressBar,
    QMessageBox, QSpinBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QIcon

from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time


class CrawlerThread(QThread):
    """크롤링 작업을 수행하는 스레드"""
    
    progress_changed = pyqtSignal(int)
    status_changed = pyqtSignal(str)
    data_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    finished_signal = pyqtSignal()
    
    def __init__(self, limit=20):
        super().__init__()
        self.limit = limit
    
    def run(self):
        try:
            self.status_changed.emit("[*] 크롤링 시작...")
            self.progress_changed.emit(10)
            
            # Selenium 설정
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            self.status_changed.emit("[*] 웹페이지 로드 중...")
            self.progress_changed.emit(25)
            
            driver.get("https://kimpga.com/")
            time.sleep(4)
            
            self.status_changed.emit("[*] 데이터 파싱 중...")
            self.progress_changed.emit(50)
            
            # 테이블 찾기
            tables = driver.find_elements(By.TAG_NAME, "table")
            
            if not tables:
                raise Exception("테이블을 찾을 수 없습니다.")
            
            coins_data = []
            table = tables[0]
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            for idx, row in enumerate(rows):
                if len(coins_data) >= self.limit:
                    break
                
                cols = row.find_elements(By.TAG_NAME, "td")
                
                if len(cols) >= 4:
                    try:
                        col0 = cols[0].text.strip()
                        col1 = cols[1].text.strip()
                        col2 = cols[2].text.strip()
                        col3 = cols[3].text.strip()
                        
                        if col0 and col1 and any(char.isdigit() for char in col1):
                            parts = col0.split()
                            
                            if len(parts) >= 2:
                                coin_symbol = parts[-1]
                                coin_name = ' '.join(parts[:-1])
                            else:
                                coin_symbol = col0
                                coin_name = col0
                            
                            coins_data.append({
                                'rank': len(coins_data) + 1,
                                'name': coin_name,
                                'symbol': coin_symbol,
                                'price': col1,
                                'change': col2,
                                'market_cap': col3
                            })
                            
                            progress = 50 + int((len(coins_data) / self.limit) * 40)
                            self.progress_changed.emit(progress)
                            self.status_changed.emit("[+] {} 추출".format(coin_name))
                    
                    except Exception as e:
                        continue
            
            driver.quit()
            
            if coins_data:
                self.progress_changed.emit(100)
                self.status_changed.emit("[+] 크롤링 완료!")
                self.data_loaded.emit(coins_data)
            else:
                raise Exception("크롤링된 데이터가 없습니다.")
        
        except Exception as e:
            error_msg = str(e)
            self.error_occurred.emit(error_msg)
            self.status_changed.emit("[!] 오류: {}".format(error_msg))
        
        finally:
            self.finished_signal.emit()


class SimpleKimpgaCrawler(QMainWindow):
    """간단한 KIMPGA 크롤러 GUI"""
    
    def __init__(self):
        super().__init__()
        self.coins_data = []
        self.crawler_thread = None
        self.init_ui()
    
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("KIMPGA 암호화폐 크롤러 - 간단 버전")
        self.setGeometry(200, 200, 1000, 600)
        
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        layout = QVBoxLayout(central_widget)
        
        # ===== 상단: 제어 패널 =====
        control_layout = QHBoxLayout()
        
        # 크롤링 개수
        control_layout.addWidget(QLabel("개수:"))
        self.spin_box = QSpinBox()
        self.spin_box.setMinimum(5)
        self.spin_box.setMaximum(100)
        self.spin_box.setValue(20)
        self.spin_box.setFixedWidth(80)
        control_layout.addWidget(self.spin_box)
        
        control_layout.addStretch()
        
        # 버튼들
        self.btn_start = QPushButton("크롤링 시작")
        self.btn_start.setFixedWidth(120)
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.btn_start.clicked.connect(self.start_crawl)
        control_layout.addWidget(self.btn_start)
        
        self.btn_save = QPushButton("저장")
        self.btn_save.setFixedWidth(80)
        self.btn_save.clicked.connect(self.save_data)
        control_layout.addWidget(self.btn_save)
        
        self.btn_clear = QPushButton("초기화")
        self.btn_clear.setFixedWidth(80)
        self.btn_clear.clicked.connect(self.clear_data)
        control_layout.addWidget(self.btn_clear)
        
        layout.addLayout(control_layout)
        
        # ===== 상태 표시 =====
        self.label_status = QLabel("준비됨")
        self.label_status.setStyleSheet("color: blue; font-weight: bold;")
        layout.addWidget(self.label_status)
        
        # ===== 진행률 바 =====
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # ===== 데이터 테이블 =====
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["순위", "코인명", "심볼", "가격", "변동률", "시가총액"])
        
        # 열 크기 조정
        for col in range(6):
            if col == 0:
                self.table.setColumnWidth(col, 50)
            elif col == 1:
                self.table.setColumnWidth(col, 180)
            elif col == 2:
                self.table.setColumnWidth(col, 80)
            else:
                self.table.setColumnWidth(col, 120)
        
        layout.addWidget(self.table)
        
        # 스타일 설정
        self.setStyleSheet("""
            QMainWindow {
                background-color: #fafafa;
            }
            QLabel {
                font-size: 10pt;
            }
            QPushButton {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                background-color: #f0f0f0;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #1976D2;
                color: white;
                padding: 5px;
                font-weight: bold;
            }
        """)
    
    def start_crawl(self):
        """크롤링 시작"""
        self.btn_start.setEnabled(False)
        self.table.setRowCount(0)
        self.progress_bar.setValue(0)
        
        limit = self.spin_box.value()
        
        # 크롤러 스레드 생성
        self.crawler_thread = CrawlerThread(limit)
        self.crawler_thread.progress_changed.connect(self.progress_bar.setValue)
        self.crawler_thread.status_changed.connect(self.update_status)
        self.crawler_thread.data_loaded.connect(self.display_data)
        self.crawler_thread.error_occurred.connect(self.show_error)
        self.crawler_thread.finished_signal.connect(self.on_finished)
        
        self.crawler_thread.start()
    
    def update_status(self, message):
        """상태 메시지 업데이트"""
        self.label_status.setText(message)
    
    def display_data(self, coins_data):
        """데이터 표시"""
        self.coins_data = coins_data
        self.table.setRowCount(len(coins_data))
        
        for row, coin in enumerate(coins_data):
            # 순위
            item = QTableWidgetItem(str(coin['rank']))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, item)
            
            # 코인명
            self.table.setItem(row, 1, QTableWidgetItem(coin['name']))
            
            # 심볼
            item = QTableWidgetItem(coin['symbol'])
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, item)
            
            # 가격
            item = QTableWidgetItem(coin['price'])
            item.setTextAlignment(Qt.AlignRight)
            self.table.setItem(row, 3, item)
            
            # 변동률 (색상 표시)
            item = QTableWidgetItem(coin['change'])
            item.setTextAlignment(Qt.AlignCenter)
            if '+' in coin['change']:
                item.setForeground(QColor('#d32f2f'))
            elif '-' in coin['change']:
                item.setForeground(QColor('#1976d2'))
            self.table.setItem(row, 4, item)
            
            # 시가총액
            item = QTableWidgetItem(coin['market_cap'])
            item.setTextAlignment(Qt.AlignRight)
            self.table.setItem(row, 5, item)
    
    def save_data(self):
        """데이터 저장"""
        if not self.coins_data:
            QMessageBox.warning(self, "경고", "저장할 데이터가 없습니다.")
            return
        
        # CSV 저장
        csv_filename = "kimpga_coins_{}.csv".format(
            datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        
        try:
            with open(csv_filename, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['rank', 'name', 'symbol', 'price', 'change', 'market_cap'])
                writer.writeheader()
                writer.writerows(self.coins_data)
            
            # JSON 저장
            json_filename = csv_filename.replace('.csv', '.json')
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(self.coins_data, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(
                self, "성공",
                "데이터가 저장되었습니다.\n\nCSV: {}\nJSON: {}".format(csv_filename, json_filename)
            )
            self.label_status.setText("데이터 저장 완료")
        
        except Exception as e:
            QMessageBox.critical(self, "오류", "저장 실패: {}".format(str(e)))
    
    def clear_data(self):
        """데이터 초기화"""
        self.coins_data = []
        self.table.setRowCount(0)
        self.progress_bar.setValue(0)
        self.label_status.setText("준비됨")
    
    def show_error(self, error_message):
        """에러 표시"""
        QMessageBox.critical(self, "오류", "크롤링 실패: {}".format(error_message))
    
    def on_finished(self):
        """크롤링 완료"""
        self.btn_start.setEnabled(True)


def main():
    app = QApplication(sys.argv)
    window = SimpleKimpgaCrawler()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
