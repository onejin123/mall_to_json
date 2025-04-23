import os
from flask import Flask
import mysql.connector
from mysql.connector import pooling

# ──────────────────────────────────────────────
# DB 헬퍼 – MySQL
# ──────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("MYSQL_HOST", "localhost"),
    "port":     int(os.getenv("MYSQL_PORT", 3306)),
    "user":     os.getenv("MYSQL_USER", "mall_user"),
    "password": os.getenv("MYSQL_PASSWORD", "mall_pass"),
    "database": os.getenv("MYSQL_DB", "Shoppingmall"),
    "charset":  "utf8mb4",
}

# 커넥션 풀 생성 (worker 수 ≥ pool_size 권장)
pool = pooling.MySQLConnectionPool(
    pool_name="mall_pool",
    pool_size=5,
    **DB_CONFIG,
)

def get_db_connection():
    """
    사용 예)
        conn = current_app.get_db_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute("SELECT 1")
            row = cur.fetchone()
    """
    conn = pool.get_connection()
    conn.autocommit = False
    return conn

# ──────────────────────────────────────────────
# 애플리케이션 팩토리
# ──────────────────────────────────────────────
def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = os.urandom(24)

    # DB 헬퍼 주입
    app.get_db_connection = staticmethod(get_db_connection)

    # ── Blueprint 등록 ─────────────────────────────────
    from blueprints.main     import main_bp
    from blueprints.auth     import auth_bp
    from blueprints.cart     import cart_bp
    from blueprints.product  import product_bp
    from blueprints.contact  import contact_bp
    from blueprints.checkout import checkout_bp
    from blueprints.admin    import admin_bp

    for bp in (
        main_bp,
        auth_bp,
        cart_bp,
        product_bp,
        contact_bp,
        checkout_bp,
    ):
        app.register_blueprint(bp)
    app.register_blueprint(admin_bp)

    # ── 전역 Jinja 컨텍스트 ────────────────────────────
    @app.context_processor
    def cart_count_processor():
        """템플릿에서 {{ cart_count }} 사용."""
        from flask import session
        cart = session.get("cart", [])
        total_items = sum(item["quantity"] for item in cart)
        return dict(cart_count=total_items)

    return app

# ──────────────────────────────────────────────
# 로컬 실행 (flask run 대신 python app.py로도 가능)
# ──────────────────────────────────────────────
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)