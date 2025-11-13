#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
KIMPGA 암호화폐 크롤러 - PyQt5 GUI 버전
https://kimpga.com/ 에서 상위 20개 코인 정보를 크롤링하는 PyQt5 기반 GUI 애플리케이션
"""

import sys
import os
import json
import csv
from datetime import datetime
from threading import Thread
from pathlib import Path

# sys.path 정리 (작업 디렉토리 충돌 방지)
if 'c:\\work' in sys.path:
    sys.path.remove('c:\\work')
work_path = os.path.dirname(os.path.abspath(__file__))
if work_path in sys.path:
    sys.path.remove(work_path)

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QProgressBar,
    QTextEdit, QFileDialog, QMessageBox, QComboBox, QSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QFont, QColor

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time


# =============================================================================
# 크롤링 워커 스레드 (메인 스레드가 멈추지 않도록)
# =============================================================================

class CrawlerSignal(QObject):
    """크롤링 진행 상황을 전송하는 신호"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    data_ready = pyqtSignal(list)
    error = pyqtSignal(str)
    finished = pyqtSignal()


class CrawlerWorker(QThread):
    """Selenium을 사용하여 데이터를 크롤링하는 워커 스레드"""
    
    def __init__(self, limit=20, headless=True):
        super().__init__()
        self.limit = limit
        self.headless = headless
        self.signal = CrawlerSignal()
        self.coins_data = []
    
    def run(self):
        """크롤링 작업 실행"""
        try:
            self.signal.status.emit("[*] 크롤링을 시작합니다...")
            self.coins_data = self.crawl_kimpga()
            
            if self.coins_data:
                self.signal.status.emit("[+] 크롤링 완료!")
                self.signal.data_ready.emit(self.coins_data)
                self.signal.progress.emit(100)
            else:
                self.signal.error.emit("크롤링 실패: 데이터를 찾을 수 없습니다.")
                
        except Exception as e:
            error_msg = "[!] 오류 발생: {}".format(str(e))
            self.signal.error.emit(error_msg)
            self.signal.status.emit(error_msg)
        finally:
            self.signal.finished.emit()
    
    def crawl_kimpga(self):
        """Selenium을 사용하여 kimpga.com에서 데이터 크롤링"""
        
        coins_data = []
        driver = None
        
        try:
            # 크롬 드라이버 설정
            self.signal.status.emit("[*] 브라우저 시작 중...")
            
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            # 웹페이지 로드
            url = "https://kimpga.com/"
            self.signal.status.emit("[*] {} 로드 중...".format(url))
            driver.get(url)
            
            # JavaScript 로드 대기
            self.signal.status.emit("[*] 페이지 로딩 대기 중...")
            time.sleep(4)
            
            # 테이블 찾기
            self.signal.status.emit("[*] 테이블 데이터 파싱 중...")
            tables = driver.find_elements(By.TAG_NAME, "table")
            
            if not tables:
                self.signal.status.emit("[!] 테이블을 찾을 수 없습니다.")
                return []
            
            self.signal.status.emit("[*] 테이블 발견: {} 개".format(len(tables)))
            
            # 첫 번째 테이블에서 데이터 추출
            table = tables[0]
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            self.signal.status.emit("[*] 테이블 행 수: {}".format(len(rows)))
            
            for idx, row in enumerate(rows):
                if len(coins_data) >= self.limit:
                    break
                
                cols = row.find_elements(By.TAG_NAME, "td")
                
                if len(cols) >= 4:
                    try:
                        # 각 셀의 텍스트 추출
                        col0_text = cols[0].text.strip()
                        col1_text = cols[1].text.strip()
                        col2_text = cols[2].text.strip()
                        col3_text = cols[3].text.strip()
                        
                        # 코인명과 심볼 분리
                        if col0_text and col1_text and any(char.isdigit() for char in col1_text):
                            parts = col0_text.split()
                            if len(parts) >= 2:
                                coin_symbol = parts[-1]
                                coin_name = ' '.join(parts[:-1])
                            else:
                                coin_symbol = col0_text
                                coin_name = col0_text
                            
                            coin_info = {
                                'rank': len(coins_data) + 1,
                                'name': coin_name,
                                'symbol': coin_symbol,
                                'price': col1_text,
                                'change': col2_text,
                                'market_cap': col3_text
                            }
                            
                            coins_data.append(coin_info)
                            
                            # 진행률 업데이트
                            progress = int((len(coins_data) / self.limit) * 100)
                            self.signal.progress.emit(progress)
                            self.signal.status.emit("[+] [{}/{}] {} 추출됨".format(
                                len(coins_data), self.limit, coin_name
                            ))
                    
                    except Exception as e:
                        print("[!] 행 {} 처리 오류: {}".format(idx, str(e)))
                        continue
            
            return coins_data
        
        except Exception as e:
            raise Exception("크롤링 중 오류 발생: {}".format(str(e)))
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass


# =============================================================================
# 메인 GUI 애플리케이션
# =============================================================================

class KimpgaCrawlerApp(QMainWindow):
    """KIMPGA 크롤러 메인 애플리케이션"""
    
    def __init__(self):
        super().__init__()
        self.coins_data = []
        self.crawler_worker = None
        self.init_ui()
    
    def init_ui(self):
        """사용자 인터페이스 초기화"""
        
        # 메인 윈도우 설정
        self.setWindowTitle("KIMPGA 암호화폐 크롤러")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(self.get_stylesheet())
        
        # 중앙 위젯 및 레이아웃
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # ===== 제어판 (상단) =====
        control_layout = QHBoxLayout()
        
        # 크롤링 개수 선택
        control_layout.addWidget(QLabel("크롤링 개수:"))
        self.spin_limit = QSpinBox()
        self.spin_limit.setMinimum(5)
        self.spin_limit.setMaximum(100)
        self.spin_limit.setValue(20)
        control_layout.addWidget(self.spin_limit)
        
        # 모드 선택
        control_layout.addWidget(QLabel("브라우저 모드:"))
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["Headless (빠름)", "일반 모드 (느림)"])
        control_layout.addWidget(self.combo_mode)
        
        control_layout.addStretch()
        
        # 크롤링 시작 버튼
        self.btn_crawl = QPushButton("시작")
        self.btn_crawl.setFixedWidth(100)
        self.btn_crawl.clicked.connect(self.start_crawling)
        self.btn_crawl.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        control_layout.addWidget(self.btn_crawl)
        
        # 중지 버튼
        self.btn_stop = QPushButton("중지")
        self.btn_stop.setFixedWidth(100)
        self.btn_stop.clicked.connect(self.stop_crawling)
        self.btn_stop.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; }")
        self.btn_stop.setEnabled(False)
        control_layout.addWidget(self.btn_stop)
        
        main_layout.addLayout(control_layout)
        
        # ===== 상태 표시 =====
        self.label_status = QLabel("준비됨. 시작 버튼을 클릭하세요.")
        self.label_status.setStyleSheet("color: #1976D2; font-weight: bold;")
        main_layout.addWidget(self.label_status)
        
        # ===== 진행률 표시 =====
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        main_layout.addWidget(self.progress_bar)
        
        # ===== 데이터 테이블 =====
        self.table_coins = QTableWidget()
        self.table_coins.setColumnCount(6)
        self.table_coins.setHorizontalHeaderLabels(
            ["순위", "코인명", "심볼", "현재가", "변동률", "시가총액"]
        )
        self.table_coins.setColumnWidth(0, 50)
        self.table_coins.setColumnWidth(1, 200)
        self.table_coins.setColumnWidth(2, 100)
        self.table_coins.setColumnWidth(3, 150)
        self.table_coins.setColumnWidth(4, 120)
        self.table_coins.setColumnWidth(5, 150)
        
        main_layout.addWidget(self.table_coins)
        
        # ===== 저장 및 로그 패널 =====
        bottom_layout = QHBoxLayout()
        
        # 저장 버튼들
        btn_save_csv = QPushButton("CSV로 저장")
        btn_save_csv.clicked.connect(self.save_csv)
        bottom_layout.addWidget(btn_save_csv)
        
        btn_save_json = QPushButton("JSON으로 저장")
        btn_save_json.clicked.connect(self.save_json)
        bottom_layout.addWidget(btn_save_json)
        
        btn_clear = QPushButton("초기화")
        btn_clear.clicked.connect(self.clear_data)
        bottom_layout.addWidget(btn_clear)
        
        main_layout.addLayout(bottom_layout)
        
        # ===== 로그 영역 =====
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(100)
        self.log_text.setStyleSheet("background-color: #f5f5f5; color: #333;")
        main_layout.addWidget(QLabel("로그:"))
        main_layout.addWidget(self.log_text)
    
    def get_stylesheet(self):
        """애플리케이션 스타일시트"""
        return """
        QMainWindow {
            background-color: #fafafa;
        }
        QLabel {
            font-size: 11pt;
            color: #333;
        }
        QPushButton {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 5px;
            background-color: #f0f0f0;
            color: #333;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #e0e0e0;
        }
        QPushButton:pressed {
            background-color: #d0d0d0;
        }
        QTableWidget {
            gridline-color: #ddd;
            background-color: white;
        }
        QHeaderView::section {
            background-color: #1976D2;
            color: white;
            padding: 5px;
            border: none;
            font-weight: bold;
        }
        """
    
    def start_crawling(self):
        """크롤링 시작"""
        self.btn_crawl.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.progress_bar.setValue(0)
        self.log_text.clear()
        self.table_coins.setRowCount(0)
        
        limit = self.spin_limit.value()
        headless = self.combo_mode.currentIndex() == 0
        
        self.log("크롤링을 시작합니다...")
        
        # 워커 스레드 생성 및 시작
        self.crawler_worker = CrawlerWorker(limit=limit, headless=headless)
        self.crawler_worker.signal.status.connect(self.log)
        self.crawler_worker.signal.progress.connect(self.update_progress)
        self.crawler_worker.signal.data_ready.connect(self.display_data)
        self.crawler_worker.signal.error.connect(self.show_error)
        self.crawler_worker.signal.finished.connect(self.on_crawling_finished)
        
        self.crawler_worker.start()
    
    def stop_crawling(self):
        """크롤링 중지"""
        if self.crawler_worker and self.crawler_worker.isRunning():
            self.crawler_worker.terminate()
            self.crawler_worker.wait()
            self.log("[*] 크롤링이 중지되었습니다.")
            self.on_crawling_finished()
    
    def on_crawling_finished(self):
        """크롤링 완료 후 처리"""
        self.btn_crawl.setEnabled(True)
        self.btn_stop.setEnabled(False)
    
    def update_progress(self, value):
        """진행률 업데이트"""
        self.progress_bar.setValue(value)
    
    def display_data(self, coins_data):
        """크롤링된 데이터를 테이블에 표시"""
        self.coins_data = coins_data
        self.table_coins.setRowCount(len(coins_data))
        
        for row, coin in enumerate(coins_data):
            # 순위
            item_rank = QTableWidgetItem(str(coin['rank']))
            item_rank.setTextAlignment(Qt.AlignCenter)
            self.table_coins.setItem(row, 0, item_rank)
            
            # 코인명
            item_name = QTableWidgetItem(coin['name'])
            self.table_coins.setItem(row, 1, item_name)
            
            # 심볼
            item_symbol = QTableWidgetItem(coin['symbol'])
            item_symbol.setTextAlignment(Qt.AlignCenter)
            self.table_coins.setItem(row, 2, item_symbol)
            
            # 현재가
            item_price = QTableWidgetItem(coin['price'])
            item_price.setTextAlignment(Qt.AlignRight)
            self.table_coins.setItem(row, 3, item_price)
            
            # 변동률 (색상 표시)
            change_text = coin['change']
            item_change = QTableWidgetItem(change_text)
            item_change.setTextAlignment(Qt.AlignCenter)
            
            # 변동률에 따라 색상 설정
            if '+' in change_text:
                item_change.setForeground(QColor('#d32f2f'))  # 빨강 (상승)
            elif '-' in change_text:
                item_change.setForeground(QColor('#1976d2'))  # 파랑 (하락)
            
            self.table_coins.setItem(row, 4, item_change)
            
            # 시가총액
            item_cap = QTableWidgetItem(coin['market_cap'])
            item_cap.setTextAlignment(Qt.AlignRight)
            self.table_coins.setItem(row, 5, item_cap)
        
        self.log("[+] {} 개의 코인 데이터가 표시되었습니다.".format(len(coins_data)))
    
    def save_csv(self):
        """CSV 파일로 저장"""
        if not self.coins_data:
            QMessageBox.warning(self, "경고", "저장할 데이터가 없습니다.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "CSV 파일 저장", "", "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=['rank', 'name', 'symbol', 'price', 'change', 'market_cap'])
                    writer.writeheader()
                    writer.writerows(self.coins_data)
                
                self.log("[+] CSV 저장 완료: {}".format(Path(file_path).name))
                QMessageBox.information(self, "성공", "CSV 파일이 저장되었습니다.")
            except Exception as e:
                self.log("[!] CSV 저장 오류: {}".format(str(e)))
                QMessageBox.critical(self, "오류", "CSV 저장 중 오류가 발생했습니다.")
    
    def save_json(self):
        """JSON 파일로 저장"""
        if not self.coins_data:
            QMessageBox.warning(self, "경고", "저장할 데이터가 없습니다.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "JSON 파일 저장", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.coins_data, f, ensure_ascii=False, indent=2)
                
                self.log("[+] JSON 저장 완료: {}".format(Path(file_path).name))
                QMessageBox.information(self, "성공", "JSON 파일이 저장되었습니다.")
            except Exception as e:
                self.log("[!] JSON 저장 오류: {}".format(str(e)))
                QMessageBox.critical(self, "오류", "JSON 저장 중 오류가 발생했습니다.")
    
    def clear_data(self):
        """데이터 초기화"""
        reply = QMessageBox.question(
            self, "확인", "모든 데이터를 초기화하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.coins_data = []
            self.table_coins.setRowCount(0)
            self.progress_bar.setValue(0)
            self.log_text.clear()
            self.label_status.setText("준비됨. 시작 버튼을 클릭하세요.")
            self.log("[*] 데이터가 초기화되었습니다.")
    
    def log(self, message):
        """로그 메시지 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = "[{}] {}".format(timestamp, message)
        
        current_text = self.log_text.toPlainText()
        if current_text:
            self.log_text.setText(current_text + "\n" + log_message)
        else:
            self.log_text.setText(log_message)
        
        # 스크롤을 맨 아래로
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
        
        # 상태 라벨 업데이트
        self.label_status.setText(message)
    
    def show_error(self, error_message):
        """에러 메시지 표시"""
        self.log(error_message)
        QMessageBox.critical(self, "오류", error_message)


# =============================================================================
# 메인 실행부
# =============================================================================

def main():
    app = QApplication(sys.argv)
    
    # 애플리케이션 스타일 설정
    app.setStyle('Fusion')
    
    # 메인 윈도우 생성 및 표시
    window = KimpgaCrawlerApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
