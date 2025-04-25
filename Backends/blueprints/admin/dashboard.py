from flask import render_template, current_app
from . import admin_bp

@admin_bp.route('/')
def dashboard():
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM products")
            prod_count = cur.fetchone()['cnt']
            cur.execute("SELECT COUNT(*) AS cnt FROM users")
            user_count = cur.fetchone()['cnt']
            cur.execute("SELECT COUNT(*) AS cnt FROM inquiries")
            inquiry_count = cur.fetchone()['cnt']
            cur.execute("SELECT COUNT(*) AS cnt FROM orders")
            order_count = cur.fetchone()['cnt']
    finally:
        conn.close()
    return render_template("admin/dashboard.html", prod_count=prod_count, user_count=user_count, inquiry_count=inquiry_count, order_count=order_count)
