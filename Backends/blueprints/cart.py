"""
shopping_web/blueprints/cart.py
장바구니 관련 라우트 모음
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app

cart_bp = Blueprint("cart_bp", __name__)

# ─────────────────────────────────────────────────────────────────────────────
# 상품 담기
# ─────────────────────────────────────────────────────────────────────────────
@cart_bp.route("/cart/add", methods=["POST"], endpoint="add_to_cart")
def add_to_cart():
    if "user_id" not in session:
        flash("로그인 후 이용 가능합니다.")
        return redirect(url_for("auth_bp.login"))

    product_id = int(request.form["product_id"])
    quantity   = int(request.form["quantity"])

    cart = session.get("cart", [])

    # 동일 상품이 있으면 수량만 증가
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            break
    else:
        cart.append({"product_id": product_id, "quantity": quantity})

    session["cart"] = cart
    return redirect(url_for("cart_bp.cart"))


# ─────────────────────────────────────────────────────────────────────────────
# 장바구니 열람
# ─────────────────────────────────────────────────────────────────────────────
@cart_bp.route("/cart", endpoint="cart")
def cart():
    if "user_id" not in session:
        flash("로그인 후 이용 가능합니다.")
        return redirect(url_for("auth_bp.login"))

    cart_items = session.get("cart", [])
    conn = current_app.get_db_connection()
    products, total_price = [], 0

    try:
        with conn.cursor(dictionary=True) as cursor:
            for item in cart_items:
                cursor.execute("""
                    SELECT
                        p.id, p.name, p.price,
                        ct.name AS type_name,
                        c.name AS category_name,
                        pi.url AS image
                    FROM products p
                    JOIN category_types ct ON p.category_type_id = ct.id
                    JOIN categories c ON ct.category_id = c.id
                    LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_primary = 1
                    WHERE p.id = %s
                """, (item["product_id"],))
                product = cursor.fetchone()

                if product:
                    qty = int(item["quantity"])
                    subtotal = product["price"] * qty
                    total_price += subtotal

                    # 🔧 이미지 경로 조립
                    image_url = url_for('static', filename=f"uploads/{product['category_name']}/{product['type_name']}/{product['image']}") \
                        if product['image'] else None

                    products.append({
                        "id":        product["id"],
                        "name":      product["name"],
                        "price":     product["price"],
                        "quantity":  qty,
                        "subtotal":  subtotal,
                        "image_url": image_url,
                    })
    finally:
        conn.close()

    return render_template("checkout/cart.html", products=products, total_price=total_price)


# ─────────────────────────────────────────────────────────────────────────────
# 수량 변경
# ─────────────────────────────────────────────────────────────────────────────
@cart_bp.route("/cart/update", methods=["POST"], endpoint="update_cart")
def update_cart():
    if "user_id" not in session:
        flash("로그인 후 이용 가능합니다.")
        return redirect(url_for("auth_bp.login"))

    product_id = int(request.form["product_id"])
    quantity   = int(request.form["quantity"])

    cart = session.get("cart", [])
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] = quantity
            break

    session["cart"] = cart
    return redirect(url_for("cart_bp.cart"))


# ─────────────────────────────────────────────────────────────────────────────
# 항목 제거
# ─────────────────────────────────────────────────────────────────────────────
@cart_bp.route("/cart/remove", methods=["POST"], endpoint="remove_from_cart")
def remove_from_cart():
    if "user_id" not in session:
        flash("로그인 후 이용 가능합니다.")
        return redirect(url_for("auth_bp.login"))

    product_id = int(request.form["product_id"])
    cart = [item for item in session.get("cart", []) if item["product_id"] != product_id]
    session["cart"] = cart
    return redirect(url_for("cart_bp.cart"))
