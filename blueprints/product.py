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
    conn     = current_app.get_db_connection()
    product  = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
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
    conn = current_app.get_db_connection()

    if category:
        products = conn.execute(
            "SELECT * FROM products WHERE category = ?",
            (category,)
        ).fetchall()
    else:
        products = conn.execute("SELECT * FROM products").fetchall()

    categories = conn.execute("SELECT DISTINCT category FROM products").fetchall()
    conn.close()

    return render_template(
        "product.html",
        products=products,
        categories=categories,
        selected=category,
    )