from flask import render_template, request, redirect, url_for, flash, current_app
from . import admin_bp

# 카테고리 타입 관리 (CRUD)
@admin_bp.route('/category_types')
def manage_category_types():
    """모든 카테고리 타입 목록 조회"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT
                  ct.id, ct.name, c.name AS category_name,
                  ct.created_at
                FROM category_types ct
                JOIN categories c ON ct.category_id = c.id
                ORDER BY c.name, ct.name
            """)
            types = cur.fetchall()
    finally:
        conn.close()
    return render_template('admin/category_types.html', types=types)


@admin_bp.route('/category_types/new', methods=('GET','POST'))
def create_category_type():
    """새 카테고리 타입 추가"""
    # GET: 폼 렌더링, POST: 저장
    conn = current_app.get_db_connection()
    # 카테고리 목록 뽑아오기 (select 박스용)
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT id, name FROM categories ORDER BY name")
        categories = cur.fetchall()

    if request.method == 'POST':
        name        = request.form['name']
        category_id = request.form['category_id']
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO category_types (name, category_id) VALUES (%s, %s)",
                    (name, category_id)
                )
            conn.commit()
            flash('카테고리 타입이 추가되었습니다.')
            return redirect(url_for('admin_bp.manage_category_types'))
        except Exception as e:
            conn.rollback()
            flash(f'추가 오류: {e}')
    conn.close()
    return render_template(
        'admin/category_type_form.html',
        categories=categories,
        action=url_for('admin_bp.create_category_type'),
        type_data=None
    )


@admin_bp.route('/category_types/<int:type_id>/edit', methods=('GET','POST'))
def edit_category_type(type_id):
    """기존 카테고리 타입 수정"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            # 수정 대상 불러오기
            cur.execute("SELECT * FROM category_types WHERE id = %s", (type_id,))
            type_data = cur.fetchone()
            cur.execute("SELECT id, name FROM categories ORDER BY name")
            categories = cur.fetchall()

        if request.method == 'POST':
            new_name        = request.form['name']
            new_category_id = request.form['category_id']
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE category_types SET name = %s, category_id = %s, updated_at = NOW() WHERE id = %s",
                    (new_name, new_category_id, type_id)
                )
            conn.commit()
            flash('카테고리 타입이 수정되었습니다.')
            return redirect(url_for('admin_bp.manage_category_types'))
    finally:
        conn.close()

    return render_template(
        'admin/category_type_form.html',
        categories=categories,
        action=url_for('admin_bp.edit_category_type', type_id=type_id),
        type_data=type_data
    )


@admin_bp.route('/category_types/<int:type_id>/delete', methods=('POST',))
def delete_category_type(type_id):
    """카테고리 타입 삭제"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM category_types WHERE id = %s", (type_id,))
        conn.commit()
        flash('카테고리 타입이 삭제되었습니다.')
    finally:
        conn.close()
    return redirect(url_for('admin_bp.manage_category_types'))