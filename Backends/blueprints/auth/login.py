from flask import render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import check_password_hash
from . import auth_bp

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