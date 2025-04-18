from flask import Blueprint, render_template, current_app

main_bp = Blueprint("main_bp", __name__)

@main_bp.route('/')
def index():
    conn = current_app.get_db_connection()
    try:
        # dictionary=True 옵션을 주면 fetchall() 결과가 dict 리스트로 들어옴
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()
    finally:
        conn.close()

    return render_template('index.html', products=products)