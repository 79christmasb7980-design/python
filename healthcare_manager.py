import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QAbstractItemView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QIcon
from datetime import datetime
from openpyxl import Workbook


class HealthcareProductManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_path = 'healthcare.db'
        self.init_database()
        self.init_ui()
        self.load_data()

    def init_database(self):
        """데이터베이스 및 테이블 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # MyProd 테이블 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS MyProd (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price INTEGER NOT NULL,
                qty INTEGER NOT NULL
            )
        ''')
        
        # 초기 샘플 데이터 추가 (데이터가 없을 경우만)
        cursor.execute('SELECT COUNT(*) FROM MyProd')
        if cursor.fetchone()[0] == 0:
            sample_data = [
                ('종합영양제', 25000, 50),
                ('비타민 C', 15000, 75),
                ('오메가3', 35000, 30),
                ('칼슘 보충제', 20000, 45),
                ('유산균 프로바이오틱스', 28000, 40)
            ]
            cursor.executemany(
                'INSERT INTO MyProd (name, price, qty) VALUES (?, ?, ?)',
                sample_data
            )
        
        conn.commit()
        conn.close()

    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle('헬스케어 제품 관리 프로그램')
        self.setGeometry(100, 100, 900, 600)
        
        # 파랑색 계열 스타일 적용
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f5ff;
            }
            QLabel {
                color: #003366;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #ffffff;
                color: #003366;
                border: 2px solid #4da6ff;
                border-radius: 4px;
                padding: 5px;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border: 2px solid #0066cc;
                background-color: #e6f2ff;
            }
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
            QPushButton:pressed {
                background-color: #003d7a;
            }
            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #e6f2ff;
                gridline-color: #4da6ff;
                border: 1px solid #4da6ff;
            }
            QTableWidget::item {
                padding: 5px;
                color: #003366;
            }
            QTableWidget::item:selected {
                background-color: #0066cc;
                color: white;
            }
            QHeaderView::section {
                background-color: #0066cc;
                color: white;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
            QMessageBox {
                background-color: #f0f5ff;
            }
            QMessageBox QLabel {
                color: #003366;
            }
        """)
        
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout()
        
        # 입력 영역 레이아웃
        input_layout = QHBoxLayout()
        
        # 제품명 입력
        name_label = QLabel('제품명:')
        name_label.setFont(QFont('Arial', 10, QFont.Bold))
        input_layout.addWidget(name_label)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('제품명을 입력하세요')
        self.name_input.returnPressed.connect(self.search_product)
        input_layout.addWidget(self.name_input)
        
        # 가격 입력
        price_label = QLabel('가격:')
        price_label.setFont(QFont('Arial', 10, QFont.Bold))
        input_layout.addWidget(price_label)
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText('가격을 입력하세요')
        self.price_input.setMaximumWidth(150)
        input_layout.addWidget(self.price_input)
        
        # 수량 입력
        qty_label = QLabel('수량:')
        qty_label.setFont(QFont('Arial', 10, QFont.Bold))
        input_layout.addWidget(qty_label)
        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText('수량을 입력하세요')
        self.qty_input.setMaximumWidth(150)
        input_layout.addWidget(self.qty_input)
        
        main_layout.addLayout(input_layout)
        
        # 버튼 영역 레이아웃
        button_layout = QHBoxLayout()
        
        # 입력 버튼
        self.add_btn = QPushButton('입력')
        self.add_btn.clicked.connect(self.add_product)
        button_layout.addWidget(self.add_btn)
        
        # 수정 버튼
        self.update_btn = QPushButton('수정')
        self.update_btn.clicked.connect(self.update_product)
        button_layout.addWidget(self.update_btn)
        
        # 삭제 버튼
        self.delete_btn = QPushButton('삭제')
        self.delete_btn.clicked.connect(self.delete_product)
        button_layout.addWidget(self.delete_btn)
        
        # 검색 버튼
        self.search_btn = QPushButton('검색')
        self.search_btn.clicked.connect(self.search_product)
        button_layout.addWidget(self.search_btn)
        
        # 초기화 버튼
        self.clear_btn = QPushButton('초기화')
        self.clear_btn.clicked.connect(self.clear_inputs)
        button_layout.addWidget(self.clear_btn)
        
        # 전체 조회 버튼
        self.all_btn = QPushButton('전체 조회')
        self.all_btn.clicked.connect(self.load_data)
        button_layout.addWidget(self.all_btn)

        # 엑셀로 저장 버튼
        self.export_btn = QPushButton('엑셀로 저장')
        self.export_btn.clicked.connect(self.export_to_excel)
        button_layout.addWidget(self.export_btn)

        main_layout.addLayout(button_layout)
        
        # 테이블 영역
        table_label = QLabel('제품 목록:')
        table_label.setFont(QFont('Arial', 11, QFont.Bold))
        table_label.setStyleSheet('color: #003366;')
        main_layout.addWidget(table_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['ID', '제품명', '가격', '수량'])
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 300)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 150)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        # 멀티 선택 허용: 드래그, Shift/Ctrl 클릭으로 여러 행 선택 가능
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # 선택 변경 시 합계 업데이트
        self.table.itemSelectionChanged.connect(self.update_totals)
        
        # 테이블 행 선택 이벤트
        self.table.itemClicked.connect(self.on_table_clicked)
        
        main_layout.addWidget(self.table)

        # 선택 합계 영역
        totals_layout = QHBoxLayout()
        totals_layout.addStretch()
        self.total_qty_label = QLabel('총 수량: 0')
        self.total_qty_label.setFont(QFont('Arial', 10, QFont.Bold))
        self.total_qty_label.setStyleSheet('color: #003366;')
        totals_layout.addWidget(self.total_qty_label)
        self.total_price_label = QLabel('총 금액: 0')
        self.total_price_label.setFont(QFont('Arial', 10, QFont.Bold))
        self.total_price_label.setStyleSheet('color: #003366; margin-left: 20px;')
        totals_layout.addWidget(self.total_price_label)
        main_layout.addLayout(totals_layout)
        
        central_widget.setLayout(main_layout)

    def load_data(self, search_term=None):
        """데이터 로드"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if search_term:
            cursor.execute(
                'SELECT * FROM MyProd WHERE name LIKE ?',
                (f'%{search_term}%',)
            )
        else:
            cursor.execute('SELECT * FROM MyProd')
        
        rows = cursor.fetchall()
        conn.close()
        
        self.table.setRowCount(len(rows))
        
        for row_idx, row in enumerate(rows):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # 직접 편집 방지
                self.table.setItem(row_idx, col_idx, item)
        # 로드 후 선택 초기화 및 합계 업데이트
        self.table.clearSelection()
        self.update_totals()

    def add_product(self):
        """제품 추가"""
        name = self.name_input.text().strip()
        price_text = self.price_input.text().strip()
        qty_text = self.qty_input.text().strip()
        
        if not name or not price_text or not qty_text:
            QMessageBox.warning(self, '경고', '모든 필드를 입력하세요.')
            return
        
        try:
            price = int(price_text)
            qty = int(qty_text)
        except ValueError:
            QMessageBox.warning(self, '경고', '가격과 수량은 숫자여야 합니다.')
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO MyProd (name, price, qty) VALUES (?, ?, ?)',
            (name, price, qty)
        )
        conn.commit()
        conn.close()
        
        QMessageBox.information(self, '성공', '제품이 추가되었습니다.')
        self.clear_inputs()
        self.load_data()

    def update_product(self):
        """제품 수정"""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, '경고', '수정할 제품을 선택하세요.')
            return
        
        product_id = int(self.table.item(selected_row, 0).text())
        name = self.name_input.text().strip()
        price_text = self.price_input.text().strip()
        qty_text = self.qty_input.text().strip()
        
        if not name or not price_text or not qty_text:
            QMessageBox.warning(self, '경고', '모든 필드를 입력하세요.')
            return
        
        try:
            price = int(price_text)
            qty = int(qty_text)
        except ValueError:
            QMessageBox.warning(self, '경고', '가격과 수량은 숫자여야 합니다.')
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE MyProd SET name = ?, price = ?, qty = ? WHERE id = ?',
            (name, price, qty, product_id)
        )
        conn.commit()
        conn.close()
        
        QMessageBox.information(self, '성공', '제품이 수정되었습니다.')
        self.clear_inputs()
        self.load_data()

    def delete_product(self):
        """제품 삭제"""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, '경고', '삭제할 제품을 선택하세요.')
            return
        
        product_id = int(self.table.item(selected_row, 0).text())
        
        reply = QMessageBox.question(
            self, '확인', '정말 삭제하시겠습니까?',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM MyProd WHERE id = ?', (product_id,))
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, '성공', '제품이 삭제되었습니다.')
            self.clear_inputs()
            self.load_data()

    def search_product(self):
        """제품 검색"""
        search_term = self.name_input.text().strip()
        if not search_term:
            QMessageBox.warning(self, '경고', '검색어를 입력하세요.')
            return
        
        self.load_data(search_term)
        QMessageBox.information(self, '검색 완료', f'"{search_term}"에 대한 검색이 완료되었습니다.')

    def clear_inputs(self):
        """입력 필드 초기화"""
        self.name_input.clear()
        self.price_input.clear()
        self.qty_input.clear()

    def on_table_clicked(self):
        """테이블 행 클릭 시 입력 필드에 값 표시"""
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            self.name_input.setText(self.table.item(selected_row, 1).text())
            self.price_input.setText(self.table.item(selected_row, 2).text())
            self.qty_input.setText(self.table.item(selected_row, 3).text())

    def update_totals(self):
        """선택된 행들의 총 수량과 총 금액을 계산하여 하단 라벨에 표시"""
        selected = self.table.selectionModel().selectedRows()
        total_qty = 0
        total_price = 0
        for idx in selected:
            row = idx.row()
            try:
                price_item = self.table.item(row, 2)
                qty_item = self.table.item(row, 3)
                if price_item is None or qty_item is None:
                    continue
                price = int(price_item.text())
                qty = int(qty_item.text())
            except Exception:
                continue
            total_qty += qty
            total_price += price * qty

        # 천 단위 구분 쉼표 적용
        self.total_qty_label.setText(f'총 수량: {total_qty:,}')
        self.total_price_label.setText(f'총 금액: {total_price:,}')

    def export_to_excel(self):
        """현재 테이블 내용을 openpyxl로 엑셀 파일로 저장"""
        # 테이블에 있는 모든 행을 대상으로 저장 (필터링된 상태면 필터된 행)
        row_count = self.table.rowCount()
        if row_count == 0:
            QMessageBox.information(self, '알림', '저장할 제품이 없습니다.')
            return

        wb = Workbook()
        ws = wb.active
        ws.title = 'Products'

        # 헤더
        headers = ['ID', '제품명', '가격', '수량']
        ws.append(headers)

        for r in range(row_count):
            row_values = []
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                row_values.append(item.text() if item is not None else '')
            ws.append(row_values)

        filename = f"products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        try:
            wb.save(filename)
            QMessageBox.information(self, '완료', f'엑셀 파일로 저장되었습니다:\n{filename}')
        except Exception as e:
            QMessageBox.critical(self, '오류', f'엑셀 저장 중 오류가 발생했습니다:\n{e}')


def main():
    app = QApplication(sys.argv)
    window = HealthcareProductManager()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
