from flask import render_template, request, redirect, url_for, flash, current_app
from werkzeug.security import generate_password_hash
from mysql.connector import errors
from . import auth_bp

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

    return render_template("login/register.html")