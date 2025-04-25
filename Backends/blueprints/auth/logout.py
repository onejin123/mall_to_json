from flask import redirect, url_for, session
from . import auth_bp

@auth_bp.route("/logout", endpoint="logout")
def logout():
    session.clear()
    return redirect(url_for("main_bp.index"))