"""
shopping_web/blueprints/auth.py
인증(Auth) 관련 라우트 모음: 회원가입·로그인·로그아웃·프로필
"""
import sqlite3
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session, current_app
)

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

        try:
            conn = current_app.get_db_connection()
            conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )
            conn.commit()
            conn.close()
            flash("회원가입이 완료되었습니다.")
            return redirect(url_for("main_bp.index"))
        except sqlite3.IntegrityError:
            flash("이미 등록된 이메일입니다.")
            return redirect(url_for("auth_bp.register"))

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
        user = conn.execute(
            "SELECT * FROM users WHERE email = ? AND password = ?",
            (email, password)
        ).fetchone()
        conn.close()

        if user:
            session["user_id"]   = user["id"]
            session["user_name"] = user["name"]
            session["is_admin"]  = user["is_admin"]
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
    conn     = current_app.get_db_connection()
    user     = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()

    return render_template("profile.html", user=user)