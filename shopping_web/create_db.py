import sqlite3

conn = sqlite3.connect('database/mall.db')
cur = conn.cursor()

# 상품 테이블 생성
cur.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    image TEXT NOT NULL
)
''')

# 샘플 상품 데이터 삽입
sample_data = [
    ('화이트 티셔츠', 19000, 'white_tshirt.jpg'),
    ('블랙 후드티', 39000, 'black_tshirt.jpg'),
    ('청바지', 29000, 'jeans.jpg')
]

cur.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

cur.executemany('INSERT INTO products (name, price, image) VALUES (?, ?, ?)', sample_data)

conn.commit()
conn.close()
