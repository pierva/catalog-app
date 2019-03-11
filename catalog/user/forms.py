from flask_wtf import FlaskForm as Form
from wtforms import TextField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo

from catalog.models import User
from sqlalchemy import exc


class LoginForm(Form):
    email = TextField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class RegisterForm(Form):
    email = TextField(
        'email',
        validators=[DataRequired(), Length(min=2, max=255)])
    password = PasswordField(
        'password',
        validators=[DataRequired(), Length(min=8, max=255)]
    )
    confirm = PasswordField(
        'Repeat password',
        validators=[
            DataRequired(),
            EqualTo('password', message="Passwords didn't match.")
        ]
    )

    admin = BooleanField('admin')

    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        try:
            user = User.query.filter_by(email=self.email.data).first()
            if user:
                self.email.errors.append("Email already registered")
                return False
            return True
        except exc.SQLAlchemyError as e:
            self.email.errors.append("Unexpected DB error")
            self.password.errors.append("Unexpected DB error")
            return False
