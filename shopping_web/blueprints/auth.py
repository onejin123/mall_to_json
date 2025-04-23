"""
shopping_web/blueprints/auth.py
인증(Auth) 관련 라우트 모음: 회원가입·로그인·로그아웃·프로필
"""
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session, current_app
)
import mysql.connector
from mysql.connector import errors

auth_bp = Blueprint("auth_bp", __name__)

# ─────────────────────────────────────────────────────────────────────────────
# 회원가입
# ─────────────────────────────────────────────────────────────────────────────
from werkzeug.security import generate_password_hash
import pymysql.err as errors

@auth_bp.route("/register", methods=["GET", "POST"], endpoint="register")
def register():
    if request.method == "POST":
        email    = request.form["email"]
        password = request.form["password"]
        nickname = request.form.get("nickname") or None
        phone    = request.form.get("phone") or None

        if not email or not password:
            flash("이메일과 비밀번호는 필수입니다.")
            return redirect(url_for("auth_bp.register"))

        hashed_pw = generate_password_hash(password)

        conn = current_app.get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (email, password, nickname, phone, role_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, (email, hashed_pw, nickname, phone, 2))  # ← role_id = 2 (일반 사용자)
            conn.commit()
            return redirect(url_for("main_bp.index"))

        except errors.IntegrityError:
            flash("이미 등록된 이메일입니다.")
            return redirect(url_for("auth_bp.register"))

        finally:
            conn.close()

    return render_template("register.html")



# ─────────────────────────────────────────────────────────────────────────────
# 로그인
# ─────────────────────────────────────────────────────────────────────────────
from werkzeug.security import check_password_hash

@auth_bp.route("/login", methods=["GET", "POST"], endpoint="login")
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = current_app.get_db_connection()
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT u.id, u.nickname, u.email, u.password, u.role_id, r.name AS role_name
                    FROM users u
                    LEFT JOIN roles r ON u.role_id = r.id
                    WHERE u.email = %s
                    """,
                    (email,)
                )
                user = cursor.fetchone()
        finally:
            conn.close()

        # 사용자 존재 여부 및 비밀번호 검증
        if user and check_password_hash(user["password"], password):
            session["user_id"]   = user["id"]
            session["user_name"] = user["nickname"]
            session["is_admin"]  = (user["role_name"] == "ADMIN")
            flash("로그인 성공!")
            return redirect(url_for("main_bp.index"))

        flash("이메일 또는 비밀번호가 올바르지 않습니다.")
        return redirect(url_for("auth_bp.login"))

    return render_template("login.html")



# ─────────────────────────────────────────────────────────────────────────────
# 로그아웃
# ─────────────────────────────────────────────────────────────────────────────
@auth_bp.route("/logout", endpoint="logout")
def logout():
    session.clear()
    return redirect(url_for("main_bp.index"))


# ─────────────────────────────────────────────────────────────────────────────
# 프로필
# ─────────────────────────────────────────────────────────────────────────────
@auth_bp.route("/profile", endpoint="profile")
def mypage():
    if "user_id" not in session:
        flash("로그인이 필요합니다.")
        return redirect(url_for("auth_bp.login"))

    tab = request.args.get("tab", "info")
    conn = current_app.get_db_connection()

    with conn.cursor(dictionary=True) as cur:
        # 사용자 정보
        cur.execute("""
            SELECT u.*, r.name AS role_name
            FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE u.id = %s
        """, (session["user_id"],))
        user = cur.fetchone()

        orders = []
        if tab == "orders":
            cur.execute("""
                SELECT o.id AS order_id, o.created_at, o.total_amount, o.status,
                       p.name AS product_name, oi.quantity, oi.unit_price
                FROM orders o
                JOIN order_items oi ON o.id = oi.order_id
                JOIN products p ON oi.product_id = p.id
                WHERE o.user_id = %s
                ORDER BY o.created_at DESC
            """, (session["user_id"],))
            raw_orders = cur.fetchall()

            # created_at 문자열을 datetime 객체로 변환
            for order in raw_orders:
                if isinstance(order["created_at"], str):
                    order["created_at"] = datetime.strptime(order["created_at"], "%Y-%m-%d %H:%M:%S")
                orders.append(order)

    conn.close()
    return render_template("profile.html", tab=tab, user=user, orders=orders)


# Existing view functions...
# ─────────────────────────────────────────────────────────────────────────────
# 주문취소
# ─────────────────────────────────────────────────────────────────────────────
from datetime import datetime
@auth_bp.route("/cancel_order/<int:order_id>", methods=["POST"], endpoint="cancel_order")
def cancel_order(order_id):
    if "user_id" not in session:
        flash("로그인이 필요합니다.")
        return redirect(url_for("auth_bp.login"))

    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            # 주문이 본인의 것인지 + 상태 확인
            cur.execute("""
                SELECT status, user_id FROM orders
                WHERE id = %s
            """, (order_id,))
            order = cur.fetchone()

            if not order or order["user_id"] != session["user_id"]:
                flash("잘못된 접근입니다.")
                return redirect(url_for("auth_bp.profile", tab="orders"))

            if order["status"] not in ("PENDING", "PAID"):
                flash("이 주문은 취소할 수 없습니다.")
                return redirect(url_for("auth_bp.profile", tab="orders"))

            # 주문 상태 업데이트
            cur.execute("""
                UPDATE orders SET status = 'CANCELLED'
                WHERE id = %s
            """, (order_id,))
            conn.commit()

            flash("주문이 취소되었습니다.")
    finally:
        conn.close()

    return redirect(url_for("auth_bp.profile", tab="orders"))

# ────────────────────────────────────────────────────────────────────────────
# 관리자: 전체 사용자 목록 조회
# ────────────────────────────────────────────────────────────────────────────
@auth_bp.route("/admin/users", endpoint="admin_users")
def admin_users():
    if not session.get("is_admin"):
        flash("관리자 권한이 필요합니다.")
        return redirect(url_for("main_bp.index"))
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT
                    u.id, u.email, u.nickname, u.phone,
                    u.role_id, r.name AS role_name,
                    u.created_at, u.updated_at
                  FROM users u
                  JOIN roles r ON u.role_id = r.id
                """
            )
            users = cursor.fetchall()
    finally:
        conn.close()
    return render_template("admin_users.html", users=users)

# ────────────────────────────────────────────────────────────────────────────
# 관리자: 사용자 권한 토글
# ────────────────────────────────────────────────────────────────────────────
@auth_bp.route("/admin/users/<int:user_id>/toggle", methods=["POST"], endpoint="toggle_user_admin")
def toggle_user_admin(user_id):
    if not session.get("is_admin"):
        flash("관리자 권한이 필요합니다.")
        return redirect(url_for("main_bp.index"))
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            # fetch all roles
            cursor.execute("SELECT id, name FROM roles")
            roles = cursor.fetchall()
            admin_role_id = next(r["id"] for r in roles if r["name"] == "ADMIN")
            user_role_id = next(r["id"] for r in roles if r["name"] == "USER")

            # fetch current user's role_id
            cursor.execute(
                "SELECT role_id FROM users WHERE id = %s",
                (user_id,)
            )
            row = cursor.fetchone()
            if row:
                new_role = user_role_id if row["role_id"] == admin_role_id else admin_role_id
                cursor.execute(
                    "UPDATE users SET role_id = %s WHERE id = %s",
                    (new_role, user_id)
                )
                conn.commit()
                flash("사용자 권한이 업데이트되었습니다.")
    finally:
        conn.close()
    return redirect(url_for("auth_bp.admin_users"))