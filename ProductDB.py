import sqlite3

class ProductDB:
    def __init__(self, db_name='MyProduct.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS Products (
            productID INTEGER PRIMARY KEY AUTOINCREMENT,
            productName TEXT NOT NULL,
            productPrice INTEGER NOT NULL
        );
        '''
        self.conn.execute(query)
        self.conn.commit()

    def insert_product(self, productName, productPrice):
        query = 'INSERT INTO Products (productName, productPrice) VALUES (?, ?);'
        self.conn.execute(query, (productName, productPrice))
        self.conn.commit()

    def update_product(self, productID, productName=None, productPrice=None):
        if productName is not None and productPrice is not None:
            query = 'UPDATE Products SET productName=?, productPrice=? WHERE productID=?;'
            self.conn.execute(query, (productName, productPrice, productID))
        elif productName is not None:
            query = 'UPDATE Products SET productName=? WHERE productID=?;'
            self.conn.execute(query, (productName, productID))
        elif productPrice is not None:
            query = 'UPDATE Products SET productPrice=? WHERE productID=?;'
            self.conn.execute(query, (productPrice, productID))
        self.conn.commit()

    def delete_product(self, productID):
        query = 'DELETE FROM Products WHERE productID=?;'
        self.conn.execute(query, (productID,))
        self.conn.commit()

    def select_products(self, limit=100):
        query = 'SELECT * FROM Products LIMIT ?;'
        cursor = self.conn.execute(query, (limit,))
        return cursor.fetchall()

    def close(self):
        self.conn.close()

if __name__ == '__main__':
    db = ProductDB()
    # 샘플 데이터 10만개 삽입
    for i in range(1, 100001):
        db.insert_product(f'Product_{i}', i * 10)
    print('샘플 데이터 10만개 삽입 완료')
    # 일부 데이터 조회
    print(db.select_products(5))
    db.close()
