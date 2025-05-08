from flask import Blueprint, jsonify, request, current_app, session, flash, redirect, url_for
import os
from pathlib import Path
from collections import defaultdict
import uuid

product_bp = Blueprint("product_bp", __name__)

@product_bp.route("/api/products", methods=["GET"])
def api_products():
    selected_category = request.args.get("category")
    selected_type = request.args.get("type")
    search_query = request.args.get("q")

    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT id, name FROM categories ORDER BY name")
            categories = cursor.fetchall()
            cursor.execute("SELECT id, category_id, name FROM category_types ORDER BY name")
            types = cursor.fetchall()

            query = """
                SELECT
                    p.id, p.name, p.description, p.price, p.stock_quantity,
                    p.created_at, p.updated_at,
                    ct.name AS type_name,
                    c.name AS category_name,
                    pi.url AS image
                FROM products p
                JOIN category_types ct ON p.category_type_id = ct.id
                JOIN categories c ON ct.category_id = c.id
                LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_primary = 1
            """
            where_clauses = []
            params = []

            if selected_category:
                category_id = next((c["id"] for c in categories if c["name"] == selected_category), None)
                if selected_type:
                    type_ids = [t["id"] for t in types if t["category_id"] == category_id and t["name"] == selected_type]
                else:
                    type_ids = [t["id"] for t in types if t["category_id"] == category_id]
                if type_ids:
                    where_clauses.append("p.category_type_id IN (" + ",".join(["%s"] * len(type_ids)) + ")")
                    params.extend(type_ids)

            if search_query:
                where_clauses.append("(p.name LIKE %s OR ct.name LIKE %s)")
                params.extend([f"%{search_query}%", f"%{search_query}%"])

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            query += " ORDER BY p.created_at DESC"

            cursor.execute(query, tuple(params))
            products = cursor.fetchall()

            for product in products:
                if product['image']:
                    product['image_path'] = f"uploads/{product['category_name']}/{product['type_name']}/{product['image']}"
                else:
                    product['image_path'] = "images/no_image.png"

    finally:
        conn.close()

    return jsonify(products)

@product_bp.route("/api/product/<int:product_id>", methods=["GET"])
def api_product_detail(product_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT
                    p.id, p.name, p.description, p.price, p.stock_quantity,
                    p.created_at, p.updated_at,
                    ct.name AS type_name,
                    c.name AS category_name,
                    pi.url AS image
                FROM products p
                JOIN category_types ct ON p.category_type_id = ct.id
                JOIN categories c ON ct.category_id = c.id
                LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.is_primary = 1
                WHERE p.id = %s
            """, (product_id,))
            product = cursor.fetchone()

            if product and product.get("image"):
                product["image_url"] = f"uploads/{product['category_name']}/{product['type_name']}/{product['image']}"
            elif product:
                product["image_url"] = "images/no_image.png"

    finally:
        conn.close()

    if product:
        return jsonify(product)
    return jsonify({"error": "Product not found"}), 404

