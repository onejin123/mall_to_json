from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, current_app
)

contact_bp = Blueprint("contact_bp", __name__)

# ─────────────────────────────────────────────────────────────────────────────
# 게시글 목록
# ─────────────────────────────────────────────────────────────────────────────
@contact_bp.route("/contact", endpoint="contact")
def contact():
    board_type = request.args.get("type", "notice")
    conn  = current_app.get_db_connection()
    posts = conn.execute(
        "SELECT * FROM posts WHERE board_type = ? ORDER BY created_at DESC",
        (board_type,)
    ).fetchall()
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
        conn.execute(
            "INSERT INTO posts (title, content, board_type, author_id) VALUES (?,?,?,?)",
            (title, content, board_type, author)
        )
        conn.commit()
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
    post = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()

    # 권한 체크
    if not post or (session["user_id"] != post["author_id"] and not session.get("is_admin")):
        flash("수정 권한이 없습니다.")
        return redirect(url_for("contact_bp.contact", type=post["board_type"]))

    conn.execute(
        "UPDATE posts SET title = ?, content = ? WHERE id = ?",
        (title, content, post_id)
    )
    conn.commit()
    conn.close()

    flash("게시글이 수정되었습니다.")
    return redirect(url_for("contact_bp.contact", type=post["board_type"]))