# catalog/category/views.py
from flask import render_template, Blueprint, request, flash, redirect, url_for, jsonify
from catalog.models import Category, Item
from sqlalchemy import exc
from catalog import db
from flask_login import login_required, current_user


category_blueprint = Blueprint('category', __name__,)


@category_blueprint.route("/catalog/api/v1/categories/JSON")
def getAllCategories():
    try:
        categories = Category.query.all()
        return jsonify(Categories=[c.serialize_category for c in categories])
    except Exception as e:
        return jsonify({"status": 500, "message": "Server error",
            "error": e})


@category_blueprint.route("/catalog/<categoryName>")
@category_blueprint.route("/catalog/<categoryName>/items")
def getCategoryItems(categoryName):
    try:
        items = Item.query.filter_by(category_name=categoryName).all()
        return render_template("partials/items-list.html", items=items,
                                user=current_user)
    except exc.SQLAlchemyError as e:
        flash({
            "message": "No category was found.",
            "role": "failure"
             })
        return redirect(url_for('main.showHome'))
    except Exception as e:
        flash({
            "message":
                "Something went wrong while processing your request.",
            "role": "failure"
            })
        return redirect(url_for('main.showHome'))


@category_blueprint.route("/catalog/new", methods=['GET', 'POST'])
@login_required
def newCategory():
    if request.method == 'GET':
        return render_template('new_category.html')
    elif request.method == 'POST':
        try:
            newCategory = Category(name = request.form['name'],
                user_id=current_user.id)
            db.session.add(newCategory)
            db.session.commit()
            flash({
                "message": "Category successfully added!",
                "role": "success"
                 })
            return redirect(url_for('main.showHome'))
        except exc.SQLAlchemyError as e:
            flash({
                "message":
                    "Something went wrong while processing your request.\n\n" +
                    e.message,
                "role": "failure"
                 })
            return redirect('/')


@category_blueprint.route("/catalog/<int:id>/edit", methods=['GET','POST'])
@login_required
def editCategory(id):
    try:
        category = Category.query.filter_by(id=id).one()
        if current_user.id == category.user_id:
            if request.method == 'POST':
                category.name = request.form['name']
                category.user_id = current_user.id
                db.session.add(category)
                db.session.commit()
                flash({
                    "message": "Category successfully updated!",
                    "role": "success"
                     })
                return redirect(url_for('main.showHome'))
            elif request.method == 'GET':
                return jsonify(category.serialize_category)
        else:
            return handleUnauthorized()
    except exc.SQLAlchemyError as e:
        flash({
            "message":
                "Something went wrong while processing your request.\n\n" +
                e.message,
            "role": "failure"
             })
        return redirect('/')


@category_blueprint.route("/catalog/<int:id>/delete", methods=['GET', 'POST'])
@login_required
def deleteCategory(id):
    try:
        category = Category.query.filter_by(id=id).first()
        if current_user.id == category.user_id:
            if request.method == 'GET':
                return jsonify(category.serialize_category)
            elif request.method == 'POST':
                items = Item.query.filter_by(category_id=id)
                items.delete(synchronize_session='evaluate')
                db.session.delete(category)
                db.session.commit()
                flash({
                    "message": "{} category deleted.".format(category.name),
                    "role": "success"
                })
                return redirect(url_for('main.showHome'))
        else:
            return handleUnauthorized()
    except exc.SQLAlchemyError as e:
        flash({
            "message": "No category was found.",
            "role": "failure"
             })
        return redirect(url_for('main.showHome'))

def handleUnauthorized():
    flash({'message': "You're not allowed to perfor this action. " +
                "please login with the account used to create " +
                "this category or with an admin account.",
           'role': 'failure'
          })
    return redirect(url_for('main.showHome'))
