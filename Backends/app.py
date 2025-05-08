from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
import os
import mysql.connector
from mysql.connector import pooling

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("MYSQL_HOST"),
    "port":     int(os.getenv("MYSQL_PORT")),
    "user":     os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DB"),
    "charset":  "utf8mb4",
}

pool = pooling.MySQLConnectionPool(
    pool_name="mall_pool",
    pool_size=5,
    **DB_CONFIG,
)

def get_db_connection():
    conn = pool.get_connection()
    conn.autocommit = False
    return conn

def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    CORS(app)

    app.get_db_connection = staticmethod(get_db_connection)

    # Blueprints
    from blueprints.main     import main_bp
    from blueprints.auth     import auth_bp
    from blueprints.cart     import cart_bp
    from blueprints.product  import product_bp
    from blueprints.contact  import contact_bp
    from blueprints.checkout import checkout_bp
    from blueprints.admin    import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp,     url_prefix="/api/auth")
    app.register_blueprint(cart_bp,     url_prefix="/api/cart")
    app.register_blueprint(product_bp)
    app.register_blueprint(contact_bp,  url_prefix="/api/contact")
    app.register_blueprint(checkout_bp, url_prefix="/api/checkout")
    app.register_blueprint(admin_bp,    url_prefix="/api/admin")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

