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
    return render_template('home.html')


@app.route("/catalog/new", methods=['GET', 'POST'])
def newCategory():
    # TODO: Come back here to redirect in case the user is not logged in
    # if 'username' not in login_session:
    #     return redirect('/login')
    if request.method == 'GET':
        return render_template('new_category.html')
    elif request.method == 'POST':
        try:
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
                "message": "Something went wrong while processing your request.",
                "role": "failure"
                 })
            return redirect('/')


@app.route("/catalog/<categoryName>/edit")
def editCategory(categoryName):
    return 'Edit {}'.format(categoryName)


@app.route("/catalog/<categoryName>/delete")
def deleteCategory(categoryName):
    return 'Delete {}'.format(categoryName)


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
