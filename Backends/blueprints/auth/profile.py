from werkzeug.security import check_password_hash, generate_password_hash
from flask import render_template, redirect, url_for, flash, session, request, current_app
from datetime import datetime
from . import auth_bp

@auth_bp.route("/profile", methods=["GET", "POST"], endpoint="profile")
def mypage():
    if "user_id" not in session:
        flash("로그인이 필요합니다.")
        return redirect(url_for("auth_bp.login"))

    if request.method == "POST":
        if request.form.get("current_password"):
            # 비밀번호 변경 처리
            current_pw = request.form.get("current_password")
            new_pw     = request.form.get("new_password")
            confirm_pw = request.form.get("confirm_password")

            conn = current_app.get_db_connection()
            try:
                with conn.cursor(dictionary=True) as cur:
                    cur.execute("SELECT password FROM users WHERE id = %s", (session["user_id"],))
                    user_pw = cur.fetchone()["password"]
                # 현재 비밀번호 확인
                if not check_password_hash(user_pw, current_pw):
                    flash("현재 비밀번호가 일치하지 않습니다.")
                    return redirect(url_for("auth_bp.profile", tab="info"))
                if new_pw != confirm_pw:
                    flash("새 비밀번호와 확인이 일치하지 않습니다.")
                    return redirect(url_for("auth_bp.profile", tab="info"))
                # 비밀번호 업데이트
                hashed = generate_password_hash(new_pw)
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE users SET password = %s, updated_at = NOW() WHERE id = %s",
                        (hashed, session["user_id"])
                    )
                conn.commit()
                flash("비밀번호가 변경되었습니다.")
            finally:
                conn.close()
            return redirect(url_for("auth_bp.profile", tab="info"))
        # 사용자 정보 업데이트
        nickname = request.form.get("nickname")
        phone    = request.form.get("phone")
        conn = current_app.get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET nickname = %s, phone = %s, updated_at = NOW() WHERE id = %s",
                    (nickname, phone, session["user_id"])
                )
            conn.commit()
            flash("개인정보가 업데이트되었습니다.")
        finally:
            conn.close()
        return redirect(url_for("auth_bp.profile", tab="info"))

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
    return render_template("login/profile.html", tab=tab, user=user, orders=orders)


# Existing view functions...
# ─────────────────────────────────────────────────────────────────────────────
# 주문취소
# ─────────────────────────────────────────────────────────────────────────────
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