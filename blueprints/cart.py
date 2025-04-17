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
    for item in cart_items:
        product = conn.execute(
            "SELECT * FROM products WHERE id = ?",
            (item["product_id"],)
        ).fetchone()

        if product:
            qty       = int(item["quantity"])
            subtotal  = product["price"] * qty
            total_price += subtotal
            products.append(
                {
                    "id":        product["id"],
                    "name":      product["name"],
                    "price":     product["price"],
                    "image":     product["image"],
                    "quantity":  qty,
                    "subtotal":  subtotal,
                }
            )
    conn.close()
    return render_template("cart.html", products=products, total_price=total_price)


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
""" 
shopping_web/blueprints/product.py
상품 리스트 & 상세 페이지
"""

""" 
shopping_web/blueprints/contact.py
게시판(공지·FAQ·QnA) 관련 라우트
"""
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, current_app
)

contact_bp = Blueprint("contact_bp", __name__)

# ─────────────────────────────────────────────────────────────────────────────
# 게시글 목록
# ─────────────────────────────────────────────────────────────────────────────
@contact_bp.route("/contact", endpoint="contact")
def contact():
    board_type = request.args.get("type", "notice")
    conn  = current_app.get_db_connection()
    posts = conn.execute(
        "SELECT * FROM posts WHERE board_type = ? ORDER BY created_at DESC",
        (board_type,)
    ).fetchall()
    conn.close()
    return render_template("contact.html", board_type=board_type, posts=posts)


# ─────────────────────────────────────────────────────────────────────────────
# 글쓰기
# ─────────────────────────────────────────────────────────────────────────────
@contact_bp.route("/contact/write", methods=["GET", "POST"], endpoint="write_post")
def write_post():
    if "user_id" not in session:
        flash("로그인이 필요합니다.")
        return redirect(url_for("auth_bp.login"))

    board_type = request.args.get("type", "qna")

    if board_type in ("notice", "faq") and not session.get("is_admin"):
        flash("접근 권한이 없습니다.")
        return redirect(url_for("contact_bp.contact", type=board_type))

    if request.method == "POST":
        title   = request.form["title"]
        content = request.form["content"]
        author  = session["user_id"]

        conn = current_app.get_db_connection()
        conn.execute(
            "INSERT INTO posts (title, content, board_type, author_id) VALUES (?,?,?,?)",
            (title, content, board_type, author)
        )
        conn.commit()
        conn.close()

        flash("글이 작성되었습니다.")
        return redirect(url_for("contact_bp.contact", type=board_type))

    return render_template("write_post.html", board_type=board_type)


# ─────────────────────────────────────────────────────────────────────────────
# 인라인 수정
# ─────────────────────────────────────────────────────────────────────────────
@contact_bp.route("/edit_post_inline", methods=["POST"], endpoint="edit_post_inline")
def edit_post_inline():
    if "user_id" not in session:
        flash("로그인이 필요합니다.")
        return redirect(url_for("auth_bp.login"))

    post_id = request.form["post_id"]
    title   = request.form["title"]
    content = request.form["content"]

    conn = current_app.get_db_connection()
    post = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()

    # 권한 체크
    if not post or (session["user_id"] != post["author_id"] and not session.get("is_admin")):
        flash("수정 권한이 없습니다.")
        return redirect(url_for("contact_bp.contact", type=post["board_type"]))

    conn.execute(
        "UPDATE posts SET title = ?, content = ? WHERE id = ?",
        (title, content, post_id)
    )
    conn.commit()
    conn.close()

    flash("게시글이 수정되었습니다.")
    return redirect(url_for("contact_bp.contact", type=post["board_type"]))