from flask import Blueprint, render_template, current_app

main_bp = Blueprint("main_bp", __name__)

@main_bp.route("/", endpoint="index")
def index():
    conn = current_app.get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return render_template("index.html", products=products)