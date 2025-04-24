"""
shopping_web/blueprints/checkout.py
결제 및 주문 처리 라우트 모음
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app

checkout_bp = Blueprint("checkout_bp", __name__)

@checkout_bp.route("/checkout", methods=["GET", "POST"], endpoint="checkout")
def checkout():
    if "user_id" not in session:
        flash("로그인이 필요합니다.")
        return redirect(url_for("auth_bp.login"))

    cart = session.get("cart", [])
    if not cart:
        flash("장바구니가 비어 있습니다.")
        return redirect(url_for("cart_bp.cart"))

    conn = current_app.get_db_connection()
    try:
        # Fetch products and compute total
        products = []
        total_price = 0
        with conn.cursor(dictionary=True) as cursor:
            for item in cart:
                cursor.execute(
                    "SELECT * FROM products WHERE id = %s",
                    (item["product_id"],)
                )
                product = cursor.fetchone()
                if product:
                    qty = int(item["quantity"])
                    subtotal = product["price"] * qty
                    total_price += subtotal
                    products.append({
                        "id":       product["id"],
                        "name":     product["name"],
                        "price":    product["price"],
                        "quantity": qty,
                        "subtotal": subtotal
                    })

        if request.method == "POST":
            address = request.form["address"]
            payment_method = request.form["payment_method"]
            user_id = session["user_id"]

            # 주문 저장
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO orders (user_id, address, payment_method, total_amount) VALUES (%s, %s, %s, %s)",
                    (user_id, address, payment_method, total_price)
                )
                order_id = cur.lastrowid

                # 상세 항목 저장
                for p in products:
                    cur.execute(
                        "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s)",
                        (order_id, p["id"], p["quantity"], p["subtotal"])
                    )
            conn.commit()
            session.pop("cart", None)
            return redirect(url_for("checkout_bp.complete", order_id=order_id))
    finally:
        conn.close()

    return render_template("checkout.html", products=products, total_price=total_price)

@checkout_bp.route("/checkout/complete/<int:order_id>", endpoint="complete")
def checkout_complete(order_id):
    if "user_id" not in session:
        flash("로그인이 필요합니다.")
        return redirect(url_for("auth_bp.login"))

    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            # 주문 정보 가져오기
            cursor.execute(
                "SELECT * FROM orders WHERE id = %s",
                (order_id,)
            )
            order = cursor.fetchone()

            # 주문 상품 목록 가져오기
            cursor.execute("""
                SELECT oi.*, p.name
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = %s
            """, (order_id,))
            items = cursor.fetchall()

            # 🔥 총 금액 계산해서 order에 추가
            if order:
                order['total_price'] = sum(item['quantity'] * item['unit_price'] for item in items)

    finally:
        conn.close()

    if not order:
        flash("주문 정보를 찾을 수 없습니다.")
        return redirect(url_for("cart_bp.cart"))

    return render_template("checkout_complete.html", order=order, items=items)

