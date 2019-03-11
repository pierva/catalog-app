#catalog/user/views.py

from flask import (render_template, Blueprint, url_for,
                   redirect, flash, request, abort)

from flask_login import login_user, logout_user, login_required, current_user

from catalog.token import generate_confirmation_token, confirm_token
from catalog.models import User
from catalog import app, db, bcrypt

from .forms import LoginForm, RegisterForm
from sqlalchemy import exc

user_blueprint = Blueprint('user', __name__,)


# User routes
@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'GET':
        return render_template('user/login.html', form=form, user=current_user)
    elif request.method == 'POST':
        if form.validate_on_submit():
            try:
                user = User.query.filter_by(email=form.email.data).first()
                if user and bcrypt.check_password_hash(
                    user.password, form.password.data):
                    login_user(user)
                    flash({'message': 'Welcome {}.'.format(user.email),
                           'role': 'success'})
                    return redirect(url_for('main.showHome'))
                else:
                    flash({'message': 'Invalid email and/or password.',
                           'role': 'failure'})
                    return render_template('user/login.html', form=form,
                                            user=current_user)
            except exc.SQLAlchemyError as e:
                flash({'message':
                        'Something went wrong while processing your request',
                       'role': 'failure'})
                return render_template('user/login.html', form=form,
                                        user=current_user)


@user_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'GET':
        return render_template('user/register.html', form=form,
                               user=current_user)
    elif request.method == 'POST':
        if form.validate_on_submit():
            try:
                user = User(
                    email=form.email.data,
                    password=form.password.data,
                    admin=form.admin.data
                )
                db.session.add(user)
                db.session.commit()
                token = generate_confirmation_token(user.email)

                login_user(user)
                flash({'message': 'New user successfully created',
                       'role': 'success'})
                return redirect(url_for("main.showHome"))
            except exc.SQLAlchemyError as e:
                flash({'message':
                        'Unexpected database error while processing ' +
                        'your request.',
                       'role': 'failure'})
                return render_template('user/register.html', form=form,
                                        user=current_user)
            except Exception as e:
                flash({'message': e, 'role': 'failure'})
                return abort(500);
        return render_template('user/register.html', form=form,
                                user=current_user)


@user_blueprint.route('/logout')
@login_required
def logout():
    try:
        logout_user()
        flash({'message': 'You were successfully logged out.',
               'role': 'success'})
        return redirect(url_for('user.login'))
    except Exception as e:
        return redirect(url_for('user.login'))
