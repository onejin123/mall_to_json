from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, current_app
)
import mysql.connector
from mysql.connector import errors
import os

contact_bp = Blueprint("contact_bp", __name__)

# ─────────────────────────────────────────────────────────────────────────────
# 게시글 목록
# ─────────────────────────────────────────────────────────────────────────────
@contact_bp.route("/contact", endpoint="contact")
def contact():
    board_type = request.args.get("type", "QNA")
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT i.*, u.nickname
                FROM inquiries i
                JOIN users u ON i.user_id = u.id
                WHERE i.type = %s
                ORDER BY i.created_at DESC
            """, (board_type,))
            posts = cursor.fetchall()
    finally:
        conn.close()

    return render_template("contact.html", board_type=board_type, posts=posts)



# ─────────────────────────────────────────────────────────────────────────────
# 글쓰기
# ─────────────────────────────────────────────────────────────────────────────
from werkzeug.utils import secure_filename

@contact_bp.route("/contact/write", methods=["GET", "POST"], endpoint="write_post")
def write_post():
    if "user_id" not in session:
        flash("로그인이 필요합니다.")
        return redirect(url_for("auth_bp.login"))

    board_type = request.args.get("type", "QNA")

    if request.method == "POST":
        title   = request.form["title"]
        content = request.form["content"]
        user_id = session["user_id"]
        file    = request.files.get("image")

        conn = current_app.get_db_connection()
        try:
            with conn.cursor() as cur:
                # 먼저 글을 insert
                cur.execute("""
                    INSERT INTO inquiries (user_id, type, title, content)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, board_type, title, content))
                conn.commit()

                # 방금 삽입된 글 id 가져오기
                cur.execute("SELECT LAST_INSERT_ID()")
                post_id = cur.fetchone()[0]

                # 이미지 업로드 처리
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    ext = os.path.splitext(filename)[1]  # .jpg, .png 등
                    save_name = f"{post_id}{ext}"
                    save_path = os.path.join(current_app.root_path, "static", "inquiries_image", save_name)

                    file.save(save_path)

                    image_db_path = f"inquiries_image/{save_name}"
                    # 이미지 경로 업데이트
                    cur.execute("UPDATE inquiries SET image_path = %s WHERE id = %s", (image_db_path, post_id))
                    conn.commit()

        finally:
            conn.close()

        flash("문의가 등록되었습니다.")
        return redirect(url_for("contact_bp.contact", type=board_type))

    return render_template("write_post.html", board_type=board_type)

# ─────────────────────────────────────────────────────────────────────────────
# 게시글 수정
# ─────────────────────────────────────────────────────────────────────────────
@contact_bp.route("/contact/edit/<int:inquiry_id>", methods=["GET", "POST"], endpoint="edit_post")
def edit_post(inquiry_id):
    if "user_id" not in session:
        flash("로그인이 필요합니다.")
        return redirect(url_for("auth_bp.login"))

    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM inquiries WHERE id = %s", (inquiry_id,))
            inquiry = cursor.fetchone()

            if not inquiry:
                flash("글을 찾을 수 없습니다.")
                return redirect(url_for("contact_bp.contact", type="QNA"))

            # 권한 체크
            if session["user_id"] != inquiry["user_id"] and not session.get("is_admin"):
                flash("수정 권한이 없습니다.")
                return redirect(url_for("contact_bp.inquiry_detail", inquiry_id=inquiry_id))

            if request.method == "POST":
                title   = request.form["title"]
                content = request.form["content"]

                cursor.execute(
                    "UPDATE inquiries SET title = %s, content = %s WHERE id = %s",
                    (title, content, inquiry_id)
                )
                conn.commit()
                flash("게시글이 수정되었습니다.")
                return redirect(url_for("contact_bp.inquiry_detail", inquiry_id=inquiry_id))
    finally:
        conn.close()

    # write_post.html 재사용
    return render_template("write_post.html", board_type=inquiry["type"], inquiry=inquiry)


# ─────────────────────────────────────────────────────────────────────────────
# 게시글 삭제
# ─────────────────────────────────────────────────────────────────────────────
@contact_bp.route("/contact/delete/<int:inquiry_id>", methods=["POST"], endpoint="delete_post")
def delete_post(inquiry_id):
    if "user_id" not in session:
        flash("로그인이 필요합니다.")
        return redirect(url_for("auth_bp.login"))

    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM inquiries WHERE id = %s", (inquiry_id,))
            inquiry = cursor.fetchone()

            if not inquiry:
                flash("게시글이 존재하지 않습니다.")
                return redirect(url_for("contact_bp.contact", type="QNA"))

            # 작성자 또는 관리자만 삭제 가능
            if session["user_id"] != inquiry["user_id"] and not session.get("is_admin"):
                flash("삭제 권한이 없습니다.")
                return redirect(url_for("contact_bp.inquiry_detail", inquiry_id=inquiry_id))

            # 첨부 이미지가 있다면 삭제
            if inquiry.get("image_path"):
                image_path = os.path.join(current_app.root_path, "static", inquiry["image_path"])
                if os.path.exists(image_path):
                    os.remove(image_path)

            cursor.execute("DELETE FROM inquiries WHERE id = %s", (inquiry_id,))
        conn.commit()
        flash("게시글이 삭제되었습니다.")
    finally:
        conn.close()

    return redirect(url_for("contact_bp.contact", type=inquiry["type"]))


# ─────────────────────────────────────────────────────────────────────────────
# 게시글 상세
# ─────────────────────────────────────────────────────────────────────────────
@contact_bp.route("/contact/inquiry/<int:inquiry_id>", endpoint="inquiry_detail")
def inquiry_detail(inquiry_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT i.*, u.nickname
                FROM inquiries i
                JOIN users u ON i.user_id = u.id
                WHERE i.id = %s
            """, (inquiry_id,))
            inquiry = cursor.fetchone()
    finally:
        conn.close()

    if not inquiry:
        flash("문의글을 찾을 수 없습니다.")
        return redirect(url_for("contact_bp.contact", type='QNA'))

    return render_template("inquiry_detail.html", inquiry=inquiry)
