from flask import Blueprint, jsonify, current_app

main_bp = Blueprint("main_bp", __name__)

@main_bp.route('/api/products/latest', methods=['GET'])
def latest_products():
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT
                    p.id, p.name, p.price,
                    pi.url AS image,
                    ct.name AS type_name,
                    c.name AS category_name
                FROM products p
                JOIN category_types ct ON p.category_type_id = ct.id
                JOIN categories c ON ct.category_id = c.id
                LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_primary = 1
                ORDER BY p.created_at DESC
                LIMIT 5
            """)
            products = cursor.fetchall()

            for p in products:
                if p["image"]:
                    p["image_path"] = f"uploads/{p['category_name']}/{p['type_name']}/{p['image']}"
                else:
                    p["image_path"] = "images/no_image.png"
    finally:
        conn.close()

    return jsonify(products)

