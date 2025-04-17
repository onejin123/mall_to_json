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
    products = []
    total_price = 0

    for item in cart:
        product = conn.execute(
            "SELECT * FROM products WHERE id = ?", (item["product_id"],)
        ).fetchone()
        if product:
            qty = int(item["quantity"])
            subtotal = product["price"] * qty
            total_price += subtotal
            products.append({
                "id": product["id"],
                "name": product["name"],
                "price": product["price"],
                "quantity": qty,
                "subtotal": subtotal
            })

    if request.method == "POST":
        address = request.form["address"]
        payment_method = request.form["payment_method"]
        user_id = session["user_id"]

        # 주문 저장
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO orders (user_id, address, payment_method, total_price)
            VALUES (?, ?, ?, ?)
        """, (user_id, address, payment_method, total_price))
        order_id = cur.lastrowid

        # 상세 항목 저장
        for p in products:
            cur.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
            """, (order_id, p["id"], p["quantity"], p["price"]))

        conn.commit()
        conn.close()

        session.pop("cart", None)
        return redirect(url_for("checkout_bp.complete", order_id=order_id))

    conn.close()
    return render_template("checkout.html", products=products, total_price=total_price)

@checkout_bp.route("/checkout/complete/<int:order_id>", endpoint="complete")
def checkout_complete(order_id):
    if "user_id" not in session:
        flash("로그인이 필요합니다.")
        return redirect(url_for("auth_bp.login"))

    conn = current_app.get_db_connection()

    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    items = conn.execute("""
        SELECT oi.*, p.name
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE order_id = ?
    """, (order_id,)).fetchall()

    conn.close()

    if not order:
        flash("주문 정보를 찾을 수 없습니다.")
        return redirect(url_for("cart_bp.cart"))

    return render_template("checkout_complete.html", order=order, items=items)
