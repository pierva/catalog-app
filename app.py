import os
import requests
from flask import (Flask, request, url_for, flash, render_template,
    redirect, jsonify, abort, make_response)

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc
from models import Base, User, Category, Item

# libraries import for user authenthication
from flask import session as login_session
import random, string

# Google oauth2 libraries
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# authenthication libraries
import httplib2
import json

CLIENT_ID = json.loads(
    open('instance/g_client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

# Python2 compatibility
try:
    range = xrange
except NameError:
    pass

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template("login.html", STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('instance/g_client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
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
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
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
        output += "Something wrong with your account. Unable to retrieve {}".format(e)
        return output

    # Check if user exists, if not, create a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 150px; height: 150px;border-radius: 75px;-webkit-border-radius: 75px;-moz-border-radius: 75px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    return output

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        flash({"message": "401: Current user not connected.",
            "role": "failure"})
        return redirect(url_for('showHome'))
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        flash({"message": "200: Successfully disconnected.", "role": "success"})
        return redirect(url_for('showHome'))
    else:
        flash({
            "message": "400: Failed to revoke token. Logout failed",
            "role": "error"
             })
        return redirect(url_for('showHome'))
        # return response

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v3.2/me"
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash({
        "messge": "Now logged in as {}".format(login_session['username']),
        "role": "success"
        })
    return output

@app.route('/disconnect')
def disconnect():
    return 'Logout page'

@app.route("/")
@app.route("/catalog")
def showHome():
    # TODO: getUserInfo from login_session and send the user info to the template
    try:
        session = DBSession()
        categories = session.query(Category).all()
        items = session.query(Item).order_by(Item.id.desc()).limit(7)
        return render_template('home.html',
            categories=categories, user=None, items=items)

    except exc.SQLAlchemyError as e:
        flash({
            "message": "Error while communicating with the db.\n\n" + e.message,
            "role": "failure"
             })
        return redirect('/')


@app.route("/catalog/new", methods=['GET', 'POST'])
def newCategory():
    # TODO: Come back here to redirect in case the user is not logged in
    # if 'username' not in login_session:
    #     return redirect('/login')
    if request.method == 'GET':
        return render_template('new_category.html')
    elif request.method == 'POST':
        try:
            session = DBSession()
            newCategory = Category(name = request.form['name'])
            session.add(newCategory)
            session.commit()
            flash({
                "message": "Category successfully added!",
                "role": "success"
                 })
            return redirect(url_for('showHome'))
        except exc.SQLAlchemyError as e:
            flash({
                "message":
                    "Something went wrong while processing your request.\n\n" +
                    e.message,
                "role": "failure"
                 })
            return redirect('/')


@app.route("/catalog/<int:id>/edit", methods=['GET','POST'])
def editCategory(id):
    try:
        session = DBSession()
        category = session.query(Category).filter_by(id=id).one()
        if request.method == 'POST':
            category.name = request.form['name']
            session.add(category)
            session.commit()
            flash({
                "message": "Category successfully updated!",
                "role": "success"
                 })
            return redirect(url_for('showHome'))
        elif request.method == 'GET':
            return jsonify(category.serialize_category)
    except exc.SQLAlchemyError as e:
        flash({
            "message":
                "Something went wrong while processing your request.\n\n" +
                e.message,
            "role": "failure"
             })
        return redirect('/')


@app.route("/catalog/<int:id>/delete", methods=['GET', 'POST'])
def deleteCategory(id):
    try:
        session = DBSession()
        category = session.query(Category).filter_by(id=id).first()
        if request.method == 'GET':
            return jsonify(category.serialize_category)
        elif request.method == 'POST':
            items = session.query(Item).filter_by(category_id=id)
            items.delete(synchronize_session='evaluate')
            session.delete(category)
            session.commit()
            flash({
                "message": "{} category deleted.".format(category.name),
                "role": "success"
            })
            return redirect(url_for('showHome'))
    except exc.SQLAlchemyError as e:
        flash({
            "message": "No category was found.",
            "role": "failure"
             })
        return redirect(url_for('showHome'))


@app.route("/catalog/<categoryName>")
@app.route("/catalog/<categoryName>/items")
def getCategoryItems(categoryName):
    try:
        session = DBSession()
        items = session.query(Item).filter_by(category_name=categoryName).all()
        return render_template("partials/items-list.html", items=items)

    except exc.SQLAlchemyError as e:
        flash({
            "message": "No category was found.",
            "role": "failure"
             })
        return redirect(url_for('showHome'))
    except Exception as e:
        flash({
            "message":
                "Something went wrong while processing your request.",
            "role": "failure"
            })
        return redirect(url_for('showHome'))


@app.route("/catalog/<categoryName>/new", methods=['GET', 'POST'])
def addCategoryItem(categoryName):
    try:
        session = DBSession()
        category = session.query(Category).filter_by(name = categoryName).one()
        if request.method == 'GET':
            return render_template('new_item.html', category=category)
        elif request.method == 'POST':
            newItem = Item(
                name = request.form['name'],
                picture = request.form['picture'],
                description = request.form['description'],
                category_id = category.id,
                category_name = category.name
            )
            session.add(newItem)
            session.commit()
            flash({
                "message": "New item successfully created.",
                "role": "success"
            })
            return redirect(url_for('showHome'))
    except exc.SQLAlchemyError as e:
        flash({
            "message":
                "No category found. Please add a category before" +
                " adding items.",
            "role": "failure"
            })
        return redirect(url_for('showHome'))


@app.route("/catalog/<categoryName>/<itemName>")
def getItem(categoryName, itemName):
    try:
        session = DBSession()
        item = session.query(Item).filter(Item.name == itemName,
            Item.category_name == categoryName).one()
        return jsonify(item.serialize_item)
    except exc.SQLAlchemyError as e:
        return jsonify({
            "message":
                "No item was found. Please retry.",
            "role": "failure"
            })
    except Exception as e:
        return redirect(url_for('showHome'))


@app.route("/catalog/<categoryName>/<itemName>/edit", methods=['GET', 'POST'])
def editCategoryItem(categoryName, itemName):
    try:
        session = DBSession()
        item = session.query(Item).filter(Item.name == itemName,
            Item.category_name == categoryName).one()
        if request.method == 'GET':
            return render_template('edit_item.html', item=item)
        elif request.method == 'POST':
            item.name = request.form['name']
            item.picture = request.form['picture']
            item.description = request.form['description']
            session.add(item)
            session.commit()
            return redirect(url_for('showHome'))
    except exc.SQLAlchemyError as e:
        flash({
            "message":
                "No item was found. Please retry.",
            "role": "failure"
            })
        return redirect(url_for('showHome'))


@app.route("/catalog/<categoryName>/<itemName>/delete", methods=['GET', 'POST'])
def deleteCategoryItem(categoryName, itemName):
    try:
        item = session.query(Item).filter(Item.name == itemName,
            Item.category_name == categoryName).one()
        if request.method == 'GET':
            return jsonify({"name": item.name, "category": item.category_name})
        elif request.method == 'POST':
            session.delete(item)
            session.commit()
            flash({
                "message": "{} deleted.".format(item.name),
                "role": "success"
            })
            return redirect(url_for('showHome'))
    except exc.SQLAlchemyError as e:
        flash({
            "message":
                "Something went wrong while processing your request.\n\n" +
                e.message,
            "role": "failure"
             })
        return redirect(url_for('showHome'))


def createUser(login_session):
    try:
        session = DBSession()
        newUser = User(name = login_session['username'],
                       email = login_session['email'],
                       picture = login_session['picture'])
        session.add(newUser)
        session.commit()
        user = session.query(User).filter_by(email = login_session['email']).one()
        return user.id
    except exc.SQLAlchemyError as e:
        return None

def getUserInfo(user_id):
    try:
        session = DBSession()
        user = session.query(User).filter_by(id= user_id).one()
        return user
    except exc.SQLAlchemyError as e:
        return None
    except Exception as e:
        return None

def getUserID(email):
    try:
        session = DBSession()
        user = session.query(User).filter_by(email= email).one()
        return user.id
    except:
        return None

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
