from flask import session, flash, redirect, url_for

def check_admin():
    if not session.get("is_admin"):
        flash("관리자 권한이 필요합니다.")
        return redirect(url_for('main_bp.index'))
