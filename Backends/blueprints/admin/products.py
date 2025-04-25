from flask import render_template, current_app, url_for
from . import admin_bp

@admin_bp.route('/products')
def manage_products():
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT
                    p.id,
                    p.name,
                    p.price,
                    cat.name AS category_name,           -- 상위 카테고리 (남자/여자 등)
                    ct.name AS type_name,                -- 하위 타입 (셔츠/팬츠 등)
                    pi.url AS image,
                    p.created_at
                FROM products p
                JOIN category_types ct ON p.category_type_id = ct.id
                JOIN categories cat ON ct.category_id = cat.id           -- ✅ 추가된 JOIN
                LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_primary = 1
                ORDER BY p.created_at DESC

            """)
            products = cur.fetchall()

            # 이미지 경로 조정
            for prod in products:
                if prod["image"]:
                    prod["image_url"] = url_for(
                        'static',
                        filename=f"uploads/{prod['category_name']}/{prod['type_name']}/{prod['image']}"
                    )
                else:
                    prod["image_url"] = url_for('static', filename="images/no-image.png")  # 대체 이미지
    finally:
        conn.close()

    return render_template("admin/products.html", products=products)

