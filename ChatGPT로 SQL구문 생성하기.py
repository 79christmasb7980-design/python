
# SQLite를 사용하여 전자제품 정보를 저장하고 관리하는 프로그램
import sqlite3
import random

# 제품 데이터베이스 관리 클래스
class ProductDB:
    def __init__(self, db_name="MyProduct.db"):
        """
        데이터베이스 연결 및 테이블 생성
        """
        self.conn = sqlite3.connect(db_name)  # DB 파일 연결
        self.create_table()  # 테이블 생성

    def create_table(self):
        """
        Products 테이블 생성 (productID: 자동 증가, productName, productPrice)
        """
        query = """
        CREATE TABLE IF NOT EXISTS Products (
            productID INTEGER PRIMARY KEY AUTOINCREMENT,
            productName TEXT NOT NULL,
            productPrice INTEGER NOT NULL
        );
        """
        self.conn.execute(query)
        self.conn.commit()

    def insert_product(self, productName, productPrice):
        """
        제품 데이터 삽입
        """
        query = "INSERT INTO Products (productName, productPrice) VALUES (?, ?);"
        self.conn.execute(query, (productName, productPrice))
        self.conn.commit()

    def update_product(self, productID, productName=None, productPrice=None):
        """
        제품 데이터 수정
        productName, productPrice 중 하나 또는 모두 변경 가능
        """
        if productName is not None and productPrice is not None:
            query = "UPDATE Products SET productName=?, productPrice=? WHERE productID=?;"
            self.conn.execute(query, (productName, productPrice, productID))
        elif productName is not None:
            query = "UPDATE Products SET productName=? WHERE productID=?;"
            self.conn.execute(query, (productName, productID))
        elif productPrice is not None:
            query = "UPDATE Products SET productPrice=? WHERE productID=?;"
            self.conn.execute(query, (productPrice, productID))
        self.conn.commit()

    def delete_product(self, productID):
        """
        제품 데이터 삭제
        """
        query = "DELETE FROM Products WHERE productID=?;"
        self.conn.execute(query, (productID,))
        self.conn.commit()

    def select_products(self, limit=10):
        """
        제품 데이터 조회 (limit 개수만큼 반환)
        """
        query = "SELECT * FROM Products LIMIT ?;"
        cursor = self.conn.execute(query, (limit,))
        return cursor.fetchall()

    def close(self):
        """
        데이터베이스 연결 종료
        """
        self.conn.close()

# 메인 실행부
if __name__ == "__main__":
    db = ProductDB()  # DB 객체 생성

    # 샘플 데이터 10만개 삽입
    sample_count = 100_000
    print("샘플 데이터 삽입 중...")
    for i in range(sample_count):
        name = f"전자제품_{i+1}"  # 제품명 생성
        price = random.randint(10000, 500000)  # 가격 랜덤 생성
        db.insert_product(name, price)  # DB에 삽입
        if (i+1) % 10000 == 0:
            print(f"{i+1}개 삽입 완료")  # 진행상황 출력

    print("샘플 데이터 삽입 완료!")

    # 일부 데이터 조회 및 출력
    print("샘플 데이터 일부 조회:")
    for row in db.select_products(5):
        print(row)

    db.close()  # DB 연결 종료