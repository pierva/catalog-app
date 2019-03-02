import os
import requests
from flask import (Flask, request, url_for, flash, render_template,
    redirect, jsonify, abort)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Category, Item
from sqlalchemy import exc


app = Flask(__name__)
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

@app.route('/login')
def showLogin():
    return 'Login page'

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
        return render_template('home.html', categories=categories, user=None)

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


@app.route("/catalog/<categoryName>/edit", methods=['GET','POST'])
def editCategory(categoryName):
    try:
        session = DBSession()
        category = session.query(Category).filter_by(name=categoryName).first()
        if request.method == 'POST':

            flash({
                "message": "Category successfully updated!",
                "role": "success"
                 })
            return redirect(url_for('showHome'))
        elif request.method == 'GET':
            # consider returning a popup here and then handle it with ajax
            return render_template('edit_category.html', category)
    except exc.SQLAlchemyError as e:
        flash({
            "message":
                "Something went wrong while processing your request.\n\n" +
                e.message,
            "role": "failure"
             })
        return redirect('/')


@app.route("/catalog/<categoryName>/delete")
def deleteCategory(categoryName):
    try:
        session = DBSession()
        category = session.query(Category).filter_by(name=categorName).first()
        # consider returning a popup here and then handly with ajax
        return render_template('edit_category.html', category)
    except exc.SQLAlchemyError as e:
        flash({
            "message":
                "Something went wrong while processing your request.\n\n" +
                e.message,
            "role": "failure"
             })


@app.route("/catalog/<categoryName>")
@app.route("/catalog/<categoryName>/items")
def getCategoryItems(categoryName):
    return 'All items for {}'.format(categoryName)


@app.route("/catalog/<categoryName>/new")
def addCategoryItem(categoryName):
    return 'Add a new item in {}'.format(categoryName)


@app.route("/catalog/<categoryName>/<itemName>")
def getItem(categoryName, itemName):
    return 'Details for {} in {}'.format(itemName, categoryName)


@app.route("/catalog/<categoryName>/<itemName>/edit")
def editCategoryItem(categoryName, itemName):
    return 'Edit {} in {}'.format(itemName, categoryName)


@app.route("/catalog/<categoryName>/<itemName>/delete")
def deleteCategoryItem(categoryName, itemName):
    return 'Delete {} in {}'.format(itemName, categoryName)


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
