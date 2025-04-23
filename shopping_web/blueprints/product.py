from flask import session, flash, redirect, url_for
import json
from pathlib import Path
from flask import Blueprint, render_template, request, current_app
import os
from werkzeug.utils import secure_filename
from collections import defaultdict
from pymysql.cursors import DictCursor

product_bp = Blueprint("product_bp", __name__)
# 업로드 디렉터리 설정 (app.py에서 UPLOAD_FOLDER 설정 권장)
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
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
                """
                SELECT
                    p.id, p.name, p.description, p.price, p.stock_quantity,
                    p.created_at, p.updated_at,
                    ct.name AS category,
                    pi.url AS image
                FROM products p
                JOIN category_types ct ON p.category_type_id = ct.id
                LEFT JOIN product_images pi
                  ON pi.product_id = p.id AND pi.is_primary = 1
                WHERE p.id = %s
                """,
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
                    ct.name AS category,
                    pi.url AS image
                FROM products p
                JOIN category_types ct ON p.category_type_id = ct.id
                LEFT JOIN product_images pi
                  ON pi.product_id = p.id AND pi.is_primary = 1
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
    finally:
        conn.close()

    return render_template(
        "product.html",
        products=products,
        selected=category,
        search_query=search_query
    )

@product_bp.route("/products/new", methods=["GET", "POST"], endpoint="create_product")
def create_product():
    if not session.get("is_admin") == 1:  # 관리자만 접근 허용
        flash("관리자 권한이 필요합니다.")
        return redirect(url_for("product_bp.products"))

    # ─────────────── GET 요청 시: 카테고리 & 타입 조회 ───────────────
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT id, name FROM categories ORDER BY name")
            categories = cursor.fetchall()

            cursor.execute("SELECT id, category_id, name FROM category_types ORDER BY name")
            types = cursor.fetchall()
    finally:
        conn.close()

    # 타입을 카테고리별로 그룹핑
    grouped = defaultdict(list)
    for t in types:
        grouped[t["category_id"]].append(t)
    for cat in categories:
        cat["types"] = grouped.get(cat["id"], [])

    # ─────────────── POST 요청 시: 상품 등록 ───────────────
    if request.method == "POST":
        name            = request.form["name"]
        category_type_id= request.form["category_type_id"]
        price           = request.form["price"]
        description     = request.form["description"]
        stock_quantity  = request.form["stock_quantity"]

        # 이미지 업로드 처리
        file = request.files.get("image")
        if not file or file.filename == "":
            flash("이미지를 업로드해주세요.")
            return redirect(url_for("product_bp.create_product"))

        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # DB에 상품 등록
        conn = current_app.get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO products (name, category_type_id, description, price, stock_quantity, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
                """, (name, category_type_id, description, price, stock_quantity))
                
                product_id = cursor.lastrowid

                # product_images 테이블이 있다면 여기에 추가
                cursor.execute("""
                    INSERT INTO product_images (product_id, url, is_primary)
                    VALUES (%s, %s, %s)
                """, (product_id, filename, 1))

            conn.commit()
        finally:
            conn.close()

        flash("상품이 등록되었습니다.")
        return redirect(url_for("product_bp.products"))

    return render_template("create_product.html", categories=categories)

@product_bp.route("/product/delete/<int:product_id>", methods=["POST"], endpoint="delete_product")
def delete_product(product_id):
    if not session.get("is_admin"):
        flash("관리자 권한이 필요합니다.")
        return redirect(url_for("product_bp.product_detail", product_id=product_id))

    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 1. order_items에서 참조 제거
            cursor.execute(
                "DELETE FROM order_items WHERE product_id = %s",
                (product_id,)
            )

            # 2. carts에서 참조 제거
            cursor.execute(
                "DELETE FROM carts WHERE product_id = %s",
                (product_id,)
            )

            # 3. product_images에서 참조 제거
            cursor.execute(
                "DELETE FROM product_images WHERE product_id = %s",
                (product_id,)
            )

            # 4. products에서 최종 삭제
            cursor.execute(
                "DELETE FROM products WHERE id = %s",
                (product_id,)
            )

        conn.commit()
    finally:
        conn.close()

    flash("상품이 완전히 삭제되었습니다.")
    return redirect(url_for("product_bp.products"))
