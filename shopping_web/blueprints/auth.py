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
@auth_bp.route("/register", methods=["GET", "POST"], endpoint="register")
def register():
    if request.method == "POST":
        name     = request.form["name"]
        email    = request.form["email"]
        password = request.form["password"]

        if not name or not email or not password:
            flash("모든 항목을 입력해주세요.")
            return redirect(url_for("auth_bp.register"))

        conn = current_app.get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                    (name, email, password)
                )
            conn.commit()
            flash("회원가입이 완료되었습니다.")
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
@auth_bp.route("/login", methods=["GET", "POST"], endpoint="login")
def login():
    if request.method == "POST":
        email    = request.form["email"]
        password = request.form["password"]

        conn = current_app.get_db_connection()
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT u.id, u.nickname AS nickname, u.email,
                        u.password, u.role_id, r.name AS role_name
                    FROM users u
                    JOIN roles r ON u.role_id = r.id
                    WHERE u.email = %s AND u.password = %s
                    """,
                    (email, password)
                )
                user = cursor.fetchone()
        finally:
            conn.close()

        if user:
            session["user_id"]   = user["id"]
            session["user_name"] = user["nickname"]
            session["is_admin"]  = (user["role_name"] == "ADMIN")
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
def profile():
    if "user_id" not in session:
        return redirect(url_for("auth_bp.login"))

    user_id = session["user_id"]
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s",
                (user_id,)
            )
            user = cursor.fetchone()
    finally:
        conn.close()

    return render_template("profile.html", user=user)

# Existing view functions...

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