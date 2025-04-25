from flask import render_template, current_app
from . import admin_bp

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
