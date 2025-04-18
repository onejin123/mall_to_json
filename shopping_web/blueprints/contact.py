from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, current_app
)
import mysql.connector
from mysql.connector import errors

contact_bp = Blueprint("contact_bp", __name__)

# ─────────────────────────────────────────────────────────────────────────────
# 게시글 목록
# ─────────────────────────────────────────────────────────────────────────────
@contact_bp.route("/contact", endpoint="contact")
def contact():
    board_type = request.args.get("type", "notice")
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(
                "SELECT * FROM inquiries WHERE type = %s ORDER BY created_at DESC",
                (board_type,)
            )
            posts = cursor.fetchall()
    finally:
        conn.close()
    return render_template("contact.html", board_type=board_type, posts=posts)


# ─────────────────────────────────────────────────────────────────────────────
# 글쓰기
# ─────────────────────────────────────────────────────────────────────────────
@contact_bp.route("/contact/write", methods=["GET", "POST"], endpoint="write_post")
def write_post():
    if "user_id" not in session:
        flash("로그인이 필요합니다.")
        return redirect(url_for("auth_bp.login"))

    board_type = request.args.get("type", "qna")

    if board_type in ("notice", "faq") and not session.get("is_admin"):
        flash("접근 권한이 없습니다.")
        return redirect(url_for("contact_bp.contact", type=board_type))

    if request.method == "POST":
        title   = request.form["title"]
        content = request.form["content"]
        author  = session["user_id"]

        conn = current_app.get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO inquiries (user_id, type, title, content) VALUES (%s, %s, %s, %s)",
                    (author, board_type, title, content)
                )
            conn.commit()
        finally:
            conn.close()

        flash("글이 작성되었습니다.")
        return redirect(url_for("contact_bp.contact", type=board_type))

    return render_template("write_post.html", board_type=board_type)


# ─────────────────────────────────────────────────────────────────────────────
# 인라인 수정
# ─────────────────────────────────────────────────────────────────────────────
@contact_bp.route("/edit_post_inline", methods=["POST"], endpoint="edit_post_inline")
def edit_post_inline():
    if "user_id" not in session:
        flash("로그인이 필요합니다.")
        return redirect(url_for("auth_bp.login"))

    post_id = request.form["post_id"]
    title   = request.form["title"]
    content = request.form["content"]

    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(
                "SELECT * FROM inquiries WHERE id = %s",
                (post_id,)
            )
            post = cursor.fetchone()

            # 권한 체크
            if not post or (session["user_id"] != post["user_id"] and not session.get("is_admin")):
                flash("수정 권한이 없습니다.")
                return redirect(url_for("contact_bp.contact", type=post["type"]))

            cursor.execute(
                "UPDATE inquiries SET title = %s, content = %s WHERE id = %s",
                (title, content, post_id)
            )
        conn.commit()
    finally:
        conn.close()

    flash("게시글이 수정되었습니다.")
    return redirect(url_for("contact_bp.contact", type=post["type"]))

@contact_bp.route("/contact/delete/<int:post_id>", methods=["POST"], endpoint="delete_post")
def delete_post(post_id):
    # 권한 체크(관리자 또는 작성자)
    if not (session.get("is_admin") or session.get("user_id") == post_id):
        flash("삭제 권한이 없습니다.")
        return redirect(url_for("contact_bp.contact", type=request.args.get("type", "qna")))

    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM inquiries WHERE id = %s",
                (post_id,)
            )
        conn.commit()
    finally:
        conn.close()
    flash("게시글이 삭제되었습니다.")
    return redirect(url_for("contact_bp.contact", type=request.args.get("type", "qna")))