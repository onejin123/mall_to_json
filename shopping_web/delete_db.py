import sqlite3

conn = sqlite3.connect('database/mall.db')
cur = conn.cursor()
table = 'products'
# 삭제할 테이블 이름 넣기 (예: users)
cur.execute(f'DROP TABLE IF EXISTS {table}')

conn.commit()
conn.close()

print(f"{table} 테이블이 삭제되었습니다.")