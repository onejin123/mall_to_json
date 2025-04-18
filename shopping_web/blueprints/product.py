from flask import session, flash, redirect, url_for
import json
from pathlib import Path
from flask import Blueprint, render_template, request, current_app

product_bp = Blueprint("product_bp", __name__)
BASE_DIR   = Path(__file__).resolve().parents[2]  # shopping_web/

# ─────────────────────────────────────────────────────────────────────────────
# 상품 상세
# ─────────────────────────────────────────────────────────────────────────────
@product_bp.route("/product/<int:product_id>", endpoint="product_detail")
def product_detail(product_id: int):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(
                "SELECT * FROM products WHERE id = %s",
                (product_id,)
            )
            product = cursor.fetchone()
    finally:
        conn.close()

    desc_path = BASE_DIR / "static" / "data" / "product_descriptions.json"
    descriptions = {}
    if desc_path.exists():
        with open(desc_path, encoding="utf-8") as f:
            descriptions = json.load(f)

    return render_template(
        "product_detail.html",
        product=product,
        desc=descriptions.get(str(product_id), {})
    )


# ─────────────────────────────────────────────────────────────────────────────
# 상품 목록 (카테고리 필터)
# ─────────────────────────────────────────────────────────────────────────────
@product_bp.route("/products", endpoint="products")
def products():
    category = request.args.get("category")
    search_query = request.args.get("q")
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            # Base query joining products and category_types
            query = """
                SELECT
                    p.id, p.name, p.description, p.price, p.stock_quantity,
                    p.created_at, p.updated_at,
                    ct.name AS category
                FROM products p
                JOIN category_types ct ON p.category_type_id = ct.id
            """
            params = []
            if search_query:
                query += " WHERE p.name LIKE %s OR ct.name LIKE %s"
                params.extend([f"%{search_query}%", f"%{search_query}%"])
            elif category:
                query += " WHERE ct.name = %s"
                params.append(category)
            query += " ORDER BY p.created_at DESC"
            cursor.execute(query, tuple(params))
            products = cursor.fetchall()

            # Fetch distinct category names for filter dropdown
            cursor.execute("""
                SELECT DISTINCT ct.name AS category
                FROM category_types ct
                JOIN products p ON p.category_type_id = ct.id
            """)
            categories = cursor.fetchall()
    finally:
        conn.close()

    return render_template(
        "product.html",
        products=products,
        categories=categories,
        selected=category,
        search_query=search_query
    )

@product_bp.route("/products/new", methods=["GET", "POST"], endpoint="create_product")
def create_product():
    if not session.get("is_admin"):
        flash("관리자 권한이 필요합니다.")
        return redirect(url_for("product_bp.products"))

    if request.method == "POST":
        name     = request.form["name"]
        category = request.form["category"]
        price    = request.form["price"]
        image    = request.form["image"]

        conn = current_app.get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO products (name, category, price, image) VALUES (%s, %s, %s, %s)",
                    (name, category, price, image)
                )
            conn.commit()
        finally:
            conn.close()

        flash("상품이 등록되었습니다.")
        return redirect(url_for("product_bp.products"))

    # GET 요청일 때만 폼 페이지 렌더
    return render_template("create_product.html")

@product_bp.route("/product/delete/<int:product_id>", methods=["POST"], endpoint="delete_product")
def delete_product(product_id):
    if not session.get("is_admin"):
        flash("관리자 권한이 필요합니다.")
        return redirect(url_for("product_bp.product_detail", product_id=product_id))

    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM products WHERE id = %s",
                (product_id,)
            )
        conn.commit()
    finally:
        conn.close()

    flash("상품이 삭제되었습니다.")
    return redirect(url_for("product_bp.products"))