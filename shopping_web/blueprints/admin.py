from flask import Blueprint, render_template, current_app, request
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

# 주문 관리
@admin_bp.route('/orders')
def manage_orders():
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT
                    o.id,
                    o.user_id,
                    u.email AS user_email,
                    o.total_amount,
                    o.status,
                    o.created_at
                FROM orders o
                JOIN users u ON o.user_id = u.id
                ORDER BY o.created_at DESC
            """)
            orders = cur.fetchall()
    finally:
        conn.close()
    return render_template("admin/orders.html", orders=orders)

@admin_bp.route('/orders/<int:order_id>')
def view_order(order_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            # Fetch order header
            cur.execute("""
                SELECT
                    o.id, o.user_id, u.email AS user_email,
                    o.total_amount, o.status, o.created_at
                FROM orders o
                JOIN users u ON o.user_id = u.id
                WHERE o.id = %s
            """, (order_id,))
            order = cur.fetchone()

            # Fetch order items
            cur.execute("""
                SELECT
                    oi.product_id, p.name AS product_name,
                    oi.quantity, oi.unit_price,
                    COALESCE(oi.subtotal, oi.unit_price * oi.quantity) AS subtotal
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = %s
            """, (order_id,))
            items = cur.fetchall()
    finally:
        conn.close()
    return render_template("admin/order_detail.html", order=order, items=items)


# 주문 상태 수정
@admin_bp.route('/orders/<int:order_id>/update', methods=['POST'])
def update_order(order_id):
    # 관리자 주문 상태 수정
    new_status = request.form.get('status')
    if not new_status:
        flash("상태를 선택해주세요.")
        return redirect(url_for('admin_bp.view_order', order_id=order_id))

    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE orders SET status = %s, updated_at = NOW() WHERE id = %s",
                (new_status, order_id)
            )
        conn.commit()
        flash("주문 상태가 업데이트되었습니다.")
    finally:
        conn.close()

    return redirect(url_for('admin_bp.view_order', order_id=order_id))

# 카테고리 타입 관리 (CRUD)
@admin_bp.route('/category_types')
def manage_category_types():
    """모든 카테고리 타입 목록 조회"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT
                  ct.id, ct.name, c.name AS category_name,
                  ct.created_at
                FROM category_types ct
                JOIN categories c ON ct.category_id = c.id
                ORDER BY c.name, ct.name
            """)
            types = cur.fetchall()
    finally:
        conn.close()
    return render_template('admin/category_types.html', types=types)


@admin_bp.route('/category_types/new', methods=('GET','POST'))
def create_category_type():
    """새 카테고리 타입 추가"""
    # GET: 폼 렌더링, POST: 저장
    conn = current_app.get_db_connection()
    # 카테고리 목록 뽑아오기 (select 박스용)
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT id, name FROM categories ORDER BY name")
        categories = cur.fetchall()

    if request.method == 'POST':
        name        = request.form['name']
        category_id = request.form['category_id']
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO category_types (name, category_id) VALUES (%s, %s)",
                    (name, category_id)
                )
            conn.commit()
            flash('카테고리 타입이 추가되었습니다.')
            return redirect(url_for('admin_bp.manage_category_types'))
        except Exception as e:
            conn.rollback()
            flash(f'추가 오류: {e}')
    conn.close()
    return render_template(
        'admin/category_type_form.html',
        categories=categories,
        action=url_for('admin_bp.create_category_type'),
        type_data=None
    )


@admin_bp.route('/category_types/<int:type_id>/edit', methods=('GET','POST'))
def edit_category_type(type_id):
    """기존 카테고리 타입 수정"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            # 수정 대상 불러오기
            cur.execute("SELECT * FROM category_types WHERE id = %s", (type_id,))
            type_data = cur.fetchone()
            cur.execute("SELECT id, name FROM categories ORDER BY name")
            categories = cur.fetchall()

        if request.method == 'POST':
            new_name        = request.form['name']
            new_category_id = request.form['category_id']
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE category_types SET name = %s, category_id = %s, updated_at = NOW() WHERE id = %s",
                    (new_name, new_category_id, type_id)
                )
            conn.commit()
            flash('카테고리 타입이 수정되었습니다.')
            return redirect(url_for('admin_bp.manage_category_types'))
    finally:
        conn.close()

    return render_template(
        'admin/category_type_form.html',
        categories=categories,
        action=url_for('admin_bp.edit_category_type', type_id=type_id),
        type_data=type_data
    )


@admin_bp.route('/category_types/<int:type_id>/delete', methods=('POST',))
def delete_category_type(type_id):
    """카테고리 타입 삭제"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM category_types WHERE id = %s", (type_id,))
        conn.commit()
        flash('카테고리 타입이 삭제되었습니다.')
    finally:
        conn.close()
    return redirect(url_for('admin_bp.manage_category_types'))