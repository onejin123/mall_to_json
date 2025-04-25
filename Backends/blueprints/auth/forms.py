from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = EmailField(
        '이메일',
        validators=[
            DataRequired(message="이메일을 입력하세요."),
            Email(message="유효한 이메일 주소를 입력하세요."),
            Length(max=100, message="100자 이하로 입력하세요.")
        ]
    )
    password = PasswordField(
        '비밀번호',
        validators=[
            DataRequired(message="비밀번호를 입력하세요."),
            Length(min=6, message="비밀번호는 최소 6자 이상이어야 합니다.")
        ]
    )
    submit = SubmitField('로그인')