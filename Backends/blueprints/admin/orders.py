from flask import render_template, request, current_app, redirect, url_for, flash
from . import admin_bp

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
