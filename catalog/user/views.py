#catalog/user/views.py
import os
import requests
from flask import (render_template, Blueprint, url_for,
                   redirect, flash, request, abort, make_response)
from flask import session as login_session
from flask_login import login_user, logout_user, login_required, current_user

from catalog.token import generate_confirmation_token, confirm_token
from catalog.models import User
from catalog import app, db, bcrypt

from .forms import LoginForm, RegisterForm
from sqlalchemy import exc
from sqlalchemy.orm import sessionmaker

import random, string

# Google oauth2 libraries
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# authenthication libraries
import httplib2
import json

user_blueprint = Blueprint('user', __name__,)


# User routes
@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
    for x in range(32))
    login_session['state'] = state
    if request.method == 'GET':
        return render_template('user/login.html', form=form,
            user=current_user, STATE=state)
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
                                            user=current_user, STATE=state)
            except exc.SQLAlchemyError as e:
                flash({'message':
                        'Something went wrong while processing your request',
                       'role': 'failure'})
                return render_template('user/login.html', form=form,
                                        user=current_user, STATE=state)


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
        if 'provider' in login_session:
            if login_session['provider'] == 'google':
                gdisconnect()
                del login_session['gplus_id']
            del login_session['username']
            del login_session['email']
            del login_session['picture']
            del login_session['user_id']
            del login_session['provider']
            flash({"message": "You have been successfully logged out.",
                   "role": "success"})
            return redirect(url_for('main.showHome'))
        else:
            logout_user()
            flash({'message': 'You were successfully logged out.',
                   'role': 'success'})
            return redirect(url_for('main.showHome'))
    except Exception as e:
        return redirect(url_for('user.login'))


@user_blueprint.route('/gconnect', methods=['POST'])
def gconnect():
    basedir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..',
        'instance'))
    CLIENT_ID = json.loads(
    open(basedir + '/g_client_secrets.json', 'r').read())['web']['client_id']
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(basedir + '/g_client_secrets.json',
            scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

        # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'.
        format(access_token))
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode('utf-8'))

        # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

        # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'),200)
        response.headers['Content-Type'] = 'application/json'
        checkAndCreateUser(login_session)
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    try:
        login_session['username'] = data['name']
        login_session['picture'] = data['picture']
        login_session['email'] = data['email']
        login_session['provider'] = 'google'
    except KeyError as e:
        output = ''
        output += "Something wrong with your account. Unable to retrieve %s" %e
        return output

    # Check if user exists, if not, create a new one
    checkAndCreateUser(login_session)

    output = ''
    output += '<h3>Welcome, '
    output += login_session['username']
    output += '!</h3>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " class = "login-picture"> '
    flash({'message': 'You are now logged in as {}'.format(
        login_session['username']), 'role': 'success'})
    return output


@user_blueprint.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token={}'.format(
        login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        try:
            deleteUser(login_session['username'])
        except exc.SQLAlchemyError as e:
            flash({'message':
                    'Unexpected database error while processing ' +
                    'your request.',
                   'role': 'failure'})
        return redirect(url_for('main.showHome'))
    else:
        flash({'message': 'Failed to revoke token. Logout failed',
            'role': 'failure'})
        return redirect(url_for('main.showHome'))


def createUser(login_session):
    try:
        newUser = User(email = login_session['email'],
                       username = login_session['username'],
                       password = ''.join(random.choice(
                        string.ascii_uppercase + string.digits)
                       for x in range(16)),
                       admin=False)
        db.session.add(newUser)
        db.session.commit()
        user = User.query.filter_by(email=login_session['email']).one()
        return user.id
    except exc.SQLAlchemyError as e:
        return None

def getUserInfo(user_id):
    try:
        user = User.query.filter_by(id= user_id).one()
        return user
    except exc.SQLAlchemyError as e:
        return None
    except Exception as e:
        return None

def getUserID(email):
    try:
        user = User.query.filter_by(email= email).one()
        return user.id
    except:
        return None

def deleteUser(username):
    try:
        user = db.session.query(User).filter_by(username=username).delete()
        db.session.commit()
        return True
    except:
        return None

def checkAndCreateUser(login_session):
    try:
        user_id = getUserID(login_session['email'])
        if not user_id:
            user_id = createUser(login_session)
            login_session['user_id'] = user_id
        login_user(getUserInfo(user_id))
        return True
    except Exception as e:
        return False
