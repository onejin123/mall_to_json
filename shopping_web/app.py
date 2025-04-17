import os
from pathlib import Path
import sqlite3
from flask import Flask

# ──────────────────────────────────────────────────────────────
# DB 헬퍼
# ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
DB_PATH  = BASE_DIR / "database" / "mall.db"

def get_db_connection():
    """SQLite 연결 헬퍼 (Row 객체 반환)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ──────────────────────────────────────────────────────────────
# 애플리케이션 팩토리
# ──────────────────────────────────────────────────────────────
def create_app() -> Flask:
    """
    Factory function – gunicorn, uWSGI 등 WSGI 서버나
    $ flask --app shopping_web.app run 에서 호출됩니다.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = os.urandom(24)

    # DB 헬퍼를 app 컨텍스트에 노출
    app.get_db_connection = staticmethod(get_db_connection)

    # ── Blueprint 등록 ─────────────────────────────────────────
    from blueprints.main     import main_bp
    from blueprints.auth     import auth_bp
    from blueprints.cart     import cart_bp
    from blueprints.product  import product_bp
    from blueprints.contact  import contact_bp

    for bp in (main_bp, auth_bp, cart_bp, product_bp, contact_bp):
        app.register_blueprint(bp)

    # ── 전역 Jinja 컨텍스트 ────────────────────────────────────
    @app.context_processor
    def cart_count_processor():
        """템플릿에서 {{ cart_count }} 로 장바구니 총 수량 사용."""
        from flask import session
        cart = session.get("cart", [])
        total_items = sum(item["quantity"] for item in cart)
        return dict(cart_count=total_items)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)