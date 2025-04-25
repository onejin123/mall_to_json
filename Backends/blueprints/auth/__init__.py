"""
shopping_web/blueprints/auth.py
인증(Auth) 관련 라우트 모음: 회원가입·로그인·로그아웃·프로필
"""
from flask import Blueprint

auth_bp = Blueprint("auth_bp", __name__)

# 기능별 route 등록
from . import register, login, logout, profile, password_reset, find_id
