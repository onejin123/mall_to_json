from flask import Blueprint, render_template, current_app
from flask import session, redirect, url_for, flash

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

@admin_bp.before_request
def check_admin():
    if not session.get("is_admin"):
        flash("관리자 권한이 필요합니다.")
        return redirect(url_for('main_bp.index'))

@admin_bp.route('/')
def dashboard():
    # 대시보드에 표시할 주요 통계나 최근 활동을 미리 뽑아서 전달
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM products")
            prod_count = cur.fetchone()['cnt']
            cur.execute("SELECT COUNT(*) AS cnt FROM users")
            user_count = cur.fetchone()['cnt']
            # 필요에 따라 주문·문의 통계 등 추가
    finally:
        conn.close()

    return render_template(
        "admin/dashboard.html",
        prod_count=prod_count,
        user_count=user_count,
    )

# 상품 관리
@admin_bp.route('/products')
def manage_products():
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT
                    p.id, p.name, p.price,
                    ct.name AS category,
                    pi.url AS image,
                    p.created_at
                FROM products p
                JOIN category_types ct ON p.category_type_id = ct.id
                LEFT JOIN product_images pi
                    ON pi.product_id = p.id AND pi.is_primary = 1
                ORDER BY p.created_at DESC
            """)
            products = cur.fetchall()
    finally:
        conn.close()
    return render_template("admin/products.html", products=products)

# 회원 관리
@admin_bp.route('/users')
def manage_users():
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT
                    u.id, u.email, u.nickname, u.phone,
                    r.name AS role_name,
                    u.created_at
                FROM users u
                JOIN roles r ON u.role_id = r.id
                ORDER BY u.created_at DESC
            """)
            users = cur.fetchall()
    finally:
        conn.close()
    return render_template("admin/users.html", users=users)

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