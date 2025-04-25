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
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash
#
# 비밀번호 재설정용 토큰 시리얼라이저
def get_serializer():
    return URLSafeTimedSerializer(current_app.secret_key)
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
# 아이디 찾기
# ─────────────────────────────────────────────────────────────────────────────
@auth_bp.route("/find_id", methods=["GET", "POST"], endpoint="find_id")
def find_id():
    if request.method == "POST":
        email = request.form.get("email")
        conn = current_app.get_db_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute("SELECT nickname FROM users WHERE email = %s", (email,))
                user = cur.fetchone()
        finally:
            conn.close()

        if user:
            flash(f"회원님의 닉네임(아이디)은 “{user['nickname']}” 입니다.")
        else:
            flash("가입된 이메일이 없습니다.")
        return redirect(url_for("auth_bp.find_id"))

    return render_template("find_id.html")


# ─────────────────────────────────────────────────────────────────────────────
# 비밀번호 재설정 요청
# ─────────────────────────────────────────────────────────────────────────────
@auth_bp.route("/reset_password_request", methods=["GET", "POST"], endpoint="reset_password_request")
def reset_password_request():
    if request.method == "POST":
        email = request.form.get("email")
        conn = current_app.get_db_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute("SELECT id FROM users WHERE email = %s", (email,))
                user = cur.fetchone()
        finally:
            conn.close()

        if not user:
            flash("등록된 이메일이 없습니다.")
            return redirect(url_for("auth_bp.reset_password_request"))

        s = get_serializer()
        token = s.dumps(email, salt="password-reset-salt")
        reset_url = url_for("auth_bp.reset_password", token=token, _external=True)
        # TODO: 실제 이메일 발송 로직 필요
        flash(f"비밀번호 재설정 링크: {reset_url}")
        return redirect(url_for("auth_bp.login"))

    return render_template("reset_password_request.html")


# ─────────────────────────────────────────────────────────────────────────────
# 비밀번호 재설정 폼 및 처리
# ─────────────────────────────────────────────────────────────────────────────
@auth_bp.route("/reset_password/<token>", methods=["GET", "POST"], endpoint="reset_password")
def reset_password(token):
    s = get_serializer()
    try:
        email = s.loads(token, salt="password-reset-salt", max_age=3600)
    except Exception:
        flash("유효하지 않거나 만료된 링크입니다.")
        return redirect(url_for("auth_bp.login"))

    if request.method == "POST":
        new_pw = request.form.get("password")
        hashed = generate_password_hash(new_pw)
        conn = current_app.get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET password = %s WHERE email = %s", (hashed, email))
            conn.commit()
            flash("비밀번호가 변경되었습니다.")
        finally:
            conn.close()
        return redirect(url_for("auth_bp.login"))

    return render_template("reset_password.html", token=token)


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