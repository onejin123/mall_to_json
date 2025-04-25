from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, current_app
)
import mysql.connector
from mysql.connector import errors
from werkzeug.utils import secure_filename
import os
from markupsafe import escape

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

    return render_template("contact/contact.html", board_type=board_type, posts=posts)


# ─────────────────────────────────────────────────────────────────────────────
# 글쓰기
# ─────────────────────────────────────────────────────────────────────────────
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

        # 관리자는 type을 선택할 수 있음
        if session.get("is_admin"):
            board_type = request.form.get("type", board_type)

        # 서버 사이드 검증
        errors = []
        title = title.strip()
        content = content.strip()
        # 제목 검증: 필수, 최대 200자
        if not title:
            errors.append("제목을 입력하세요.")
        elif len(title) > 200:
            errors.append("제목은 200자 이하로 입력해야 합니다.")
        # 내용 검증: 필수, 최대 2000자
        if not content:
            errors.append("내용을 입력하세요.")
        elif len(content) > 2000:
            errors.append("내용은 2000자 이하로 입력해야 합니다.")
        # 게시판 타입 검증
        allowed_types = ["NOTICE", "FAQ", "QNA"]
        if board_type not in allowed_types:
            errors.append("유효하지 않은 게시판 타입입니다.")

        if errors:
            for e in errors:
                flash(e)
            return render_template(
                "contact/write_post.html",
                board_type=board_type,
                title=escape(title),
                content=escape(content)
            )

        conn = current_app.get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO inquiries (user_id, type, title, content)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, board_type, title, content))
                conn.commit()

                cur.execute("SELECT LAST_INSERT_ID()")
                post_id = cur.fetchone()[0]

                if file and file.filename:
                    # 파일 이름과 확장자 처리
                    filename = secure_filename(file.filename)
                    ext = os.path.splitext(filename)[1]
                    save_name = f"{post_id}{ext}"
                    
                    # 상대 경로로 저장 경로 설정 (Flask 앱의 root_path를 기준으로)
                    save_path = os.path.join("C:\\Users\\user\\Desktop\\web2\\secutity_web", "Fronts", "static", "inquiries_image", save_name)
                    print(save_path)
                    # 디렉터리가 존재하지 않으면 생성
                    directory = os.path.dirname(save_path)
                    if not os.path.exists(directory):
                        os.makedirs(directory)

                    # 파일 저장
                    file.save(save_path)

                    # DB 경로 업데이트 (상대 경로)
                    image_db_path = f"inquiries_image/{save_name}"  # DB에 저장할 상대 경로
                    cur.execute("UPDATE inquiries SET image_path = %s WHERE id = %s", (image_db_path, post_id))
                    conn.commit()
        finally:
            conn.close()

        
        return redirect(url_for("contact_bp.contact", type=board_type))

    return render_template("contact/write_post.html", board_type=board_type)


# 게시글 수정
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

            if session["user_id"] != inquiry["user_id"] and not session.get("is_admin"):
                flash("수정 권한이 없습니다.")
                return redirect(url_for("contact_bp.inquiry_detail", inquiry_id=inquiry_id))

            if request.method == "POST":
                title = request.form["title"]
                content = request.form["content"]
                file = request.files.get("image")

                # 서버 사이드 검증
                errors = []
                title = title.strip()
                content = content.strip()
                if not title:
                    errors.append("제목을 입력하세요.")
                elif len(title) > 200:
                    errors.append("제목은 200자 이하로 입력해야 합니다.")
                if not content:
                    errors.append("내용을 입력하세요.")
                elif len(content) > 2000:
                    errors.append("내용은 2000자 이하로 입력해야 합니다.")
                if errors:
                    for e in errors:
                        flash(e)
                    return render_template(
                        "contact/write_post.html",
                        board_type=inquiry["type"],
                        inquiry=inquiry,
                        title=escape(title),
                        content=escape(content)
                    )

                # 이미지 처리: 기존 이미지 삭제 후 새 이미지 저장
                if file and file.filename:
                    # 기존 이미지 삭제
                    if inquiry.get("image_path"):
                        image_path = os.path.join(current_app.root_path, "static", inquiry["image_path"])
                        if os.path.exists(image_path):
                            os.remove(image_path)

                    # 파일 이름과 확장자 처리
                    filename = secure_filename(file.filename)
                    ext = os.path.splitext(filename)[1]
                    save_name = f"{inquiry_id}{ext}"

                    # 상대 경로로 저장 경로 설정
                    save_path = os.path.join(current_app.root_path, "Fronts", "static", "inquiries_image", save_name)

                    # 디렉터리가 존재하지 않으면 생성
                    directory = os.path.dirname(save_path)
                    if not os.path.exists(directory):
                        os.makedirs(directory)

                    # 파일 저장
                    file.save(save_path)

                    # DB 경로 업데이트
                    image_db_path = f"./static/inquiries_image/{save_name}"
                    cursor.execute("UPDATE inquiries SET image_path = %s WHERE id = %s", (image_db_path, inquiry_id))
                    conn.commit()

                # 제목과 내용 업데이트
                cursor.execute("UPDATE inquiries SET title = %s, content = %s WHERE id = %s",
                               (title, content, inquiry_id))
                conn.commit()

                flash("게시글이 수정되었습니다.")
                return redirect(url_for("contact_bp.inquiry_detail", inquiry_id=inquiry_id))
    finally:
        conn.close()

    return render_template("contact/write_post.html", board_type=inquiry["type"], inquiry=inquiry)



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

            if session["user_id"] != inquiry["user_id"] and not session.get("is_admin"):
                flash("삭제 권한이 없습니다.")
                return redirect(url_for("contact_bp.inquiry_detail", inquiry_id=inquiry_id))

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

    return render_template("contact/inquiry_detail.html", inquiry=inquiry)
