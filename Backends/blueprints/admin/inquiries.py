from flask import render_template, current_app
from . import admin_bp

# 문의 관리
@admin_bp.route('/inquiries')
def manage_inquiries():
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT
                    i.id, i.title, i.type AS inquiry_type,
                    u.nickname AS author,
                    i.created_at
                FROM inquiries i
                JOIN users u ON i.user_id = u.id
                ORDER BY i.created_at DESC
            """)
            inquiries = cur.fetchall()
    finally:
        conn.close()
    return render_template("admin/inquiries.html", inquiries=inquiries)
