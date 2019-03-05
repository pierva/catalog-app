import os
import requests
from flask import (Flask, request, url_for, flash, render_template,
    redirect, jsonify, abort)
from sqlalchemy import create_engine, and_
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
            session.delete(category)
            session.commit()
            flash({
                "message": "{} category deleted.".format(category.name),
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


@app.route("/catalog/<categoryName>")
@app.route("/catalog/<categoryName>/items")
def getCategoryItems(categoryName):
    return 'All items for {}'.format(categoryName)


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
    return 'Details for {} in {}'.format(itemName, categoryName)


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


@app.route("/catalog/<categoryName>/<itemName>/delete")
def deleteCategoryItem(categoryName, itemName):
    return 'Delete {} in {}'.format(itemName, categoryName)


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
