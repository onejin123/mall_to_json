from flask import render_template, current_app, session, redirect, url_for, flash
from . import admin_bp

@admin_bp.route('/users')
def manage_users():
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT u.id, u.email, u.nickname, u.phone,
                       r.name AS role_name, u.created_at, u.updated_at
                FROM users u
                JOIN roles r ON u.role_id = r.id
                ORDER BY u.created_at DESC
            """)
            users = cur.fetchall()
    finally:
        conn.close()
    return render_template("admin/users.html", users=users)
# ─────────────────────────────────────────────────────────────────────────────
# 사용자 권한 토글 (관리자 <-> 일반 사용자)
# ─────────────────────────────────────────────────────────────────────────────
@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"], endpoint="toggle_user_admin")
def toggle_user_admin(user_id):
    if not session.get("is_admin"):
        flash("관리자 권한이 필요합니다.")
        return redirect(url_for("main_bp.index"))

    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            # 역할 정보 가져오기
            cursor.execute("SELECT id, name FROM roles")
            roles = cursor.fetchall()
            admin_role_id = next(r["id"] for r in roles if r["name"] == "ADMIN")
            user_role_id = next(r["id"] for r in roles if r["name"] == "USER")

            # 현재 사용자 역할 확인
            cursor.execute("SELECT role_id FROM users WHERE id = %s", (user_id,))
            row = cursor.fetchone()

            if row:
                new_role_id = user_role_id if row["role_id"] == admin_role_id else admin_role_id
                cursor.execute("UPDATE users SET role_id = %s WHERE id = %s", (new_role_id, user_id))
                conn.commit()
                flash("사용자 권한이 업데이트되었습니다.")
    finally:
        conn.close()

    return redirect(url_for("admin_bp.manage_users"))