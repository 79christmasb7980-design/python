#db1.py

import sqlite3
#연결 개체
#영구적으로 파일에 저장
con = sqlite3.connect(r"c:\work\test.db")  #메모리 DB : test ":memory:" 로 지정하고 정상인 경우 db 로 저장
#커서 개체
cursor = con.cursor()  
#테이블 생성 (ANSI SQL99 표준문법)
cursor.execute("CREATE TABLE IF NOT EXISTS PhonBook (name text, phoneNum text);")

#데이터 삽입
cursor.execute("INSERT INTO PhonBook VALUES ('홍길동', '010-1234-5678');")
cursor.execute("INSERT INTO PhonBook VALUES ('김철수', '010-9876-5432');")

#입력 값으로 삽입
name = "이영희"
phoneNum = "010-5555-6666"
cursor.execute("INSERT INTO PhonBook (name, phoneNum) VALUES (?, ?);", (name, phoneNum))

#여러 값 삽입
dataList = [
    ('박민수', '010-1111-2222'),
    ('최지은', '010-3333-4444'),
    ('강다은', '010-7777-8888')
]
cursor.executemany("INSERT INTO PhonBook (name, phoneNum) VALUES (?, ?);", dataList) #(( )) 이차원 배열

#검색
#for row in cursor.execute("SELECT * FROM PhonBook;"):
#    print(row)

#패치메서드 호출
cursor.execute("SELECT * FROM PhonBook;")
print("---fetchone()---")
print(cursor.fetchone())  #한 행만 반환
print("---fetchmany(2)---")
print(cursor.fetchmany(2))  #지정한 개수만큼 반환
print("---fetchall()---")
cursor.execute("SELECT * FROM PhonBook;")
print(cursor.fetchall())  #모든 행 반환
