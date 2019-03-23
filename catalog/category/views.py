# catalog/category/views.py

from flask import (render_template, Blueprint, request, flash,
                   redirect, url_for, jsonify)
from catalog.models import Category, Item
from sqlalchemy import exc
from catalog import db
from flask_login import login_required, current_user


category_blueprint = Blueprint('category', __name__,)


@category_blueprint.route("/catalog/api/v1/categories/JSON")
def getAllCategories():
    """Get all the categories API endpoint

    This endpoints allows to get all the categories present in the database.
    No parameters are required.
    The returned json will contain a list accessible from the "Categories" key.
    Each object inside the list, will contain the id of the category,
    the category name and the id of the user that created the category.
    """
    try:
        categories = Category.query.all()
        return jsonify(Categories=[c.serialize_category for c in categories])
    except Exception as e:
        return jsonify({"status": 500, "message": "Server error",
                        "error": e})


@category_blueprint.route("/catalog/<categoryName>")
@category_blueprint.route("/catalog/<categoryName>/items")
def getCategoryItems(categoryName):
    """Get the items in a specifc category

    With this API endpoint you can get a list of all the items present in
    the specific category passed as parameter.
    The category name must match exactly the one present in the database.
    The list of returned JSON objects can be accessed through the key "Items".
    Each object in the list will contain the:
        category_id,
        category_name,
        description,
        id (of the item),
        name,
        picture (uri),
        user_id (creator of the item).
    """
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
            if request.form['name']:
                newCategory = Category(name=request.form['name'],
                                       user_id=current_user.id)
                db.session.add(newCategory)
                db.session.commit()
                flash({
                    "message": "Category successfully added!",
                    "role": "success"
                     })
            else:
                flash({
                    "message": "Category name cannot be empty!",
                    "role": "failure"
                     })
            return redirect(url_for('main.showHome'))
        except exc.SQLAlchemyError as e:
            flash({
                "message":
                    "Something went wrong while processing your request.",
                "role": "failure"
                 })
            return redirect('/')


@category_blueprint.route("/catalog/<int:id>/edit", methods=['GET', 'POST'])
@login_required
def editCategory(id):
    try:
        category = Category.query.filter_by(id=id).one()
        if current_user.id == category.user_id or current_user.admin:
            if request.method == 'POST':
                if request.form['name']:
                    category.name = request.form['name']
                    category.user_id = current_user.id
                    db.session.add(category)
                    db.session.commit()
                    flash({
                        "message": "Category successfully updated!",
                        "role": "success"
                         })
                else:
                    flash({
                        "message": "Category name cannot be empty!",
                        "role": "failure"
                         })
                return redirect(url_for('main.showHome'))
            elif request.method == 'GET':
                return jsonify(category.serialize_category)
        else:
            return handleUnauthorized()
    except exc.SQLAlchemyError as e:
        flash({
            "message":
                "Something went wrong while processing your request.",
            "role": "failure"
             })
        return redirect('/')


@category_blueprint.route("/catalog/<int:id>/delete", methods=['GET', 'POST'])
@login_required
def deleteCategory(id):
    try:
        category = Category.query.filter_by(id=id).first()
        if current_user.id == category.user_id or current_user.admin:
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
    flash({
        'message': "You're not allowed to perfor this action. " +
                   "please login with the account used to create " +
                   "this category or with an admin account.",
        'role': 'failure'
          })
    return redirect(url_for('main.showHome'))
