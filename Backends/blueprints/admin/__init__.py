from flask import Blueprint
from .utils import check_admin

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')
admin_bp.before_request(check_admin)

# 경로 임포트만으로 자동 등록됨
from . import dashboard, products, users, orders, inquiries, category_types
