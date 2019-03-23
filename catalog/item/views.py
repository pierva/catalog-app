# catalog/item/views.py

from flask import (render_template, Blueprint, request, flash,
                   redirect, url_for, jsonify)
from catalog.models import Category, Item
from sqlalchemy import exc
from catalog import db
from flask_login import current_user, login_required

item_blueprint = Blueprint('item', __name__,)


@item_blueprint.route("/catalog/api/v1/all/JSON")
def getItemsJSON():
    """Get all the items info API endpoint

        This API endpoint provides a GET method to query all the data in the
        database.
        This route doesn't require any parameter nor authentication.
        The JSON object returned by the API route will contain a list of
        items accessible with the key "Items."
        Each item object inside the list will have the following keys:
            category_id,
            category_name,
            description,
            id (of the item),
            name,
            picture,
            user_id (creator of the item)

        In case of error an object is returned with the following keys:
            status (error code),
            error (error message)
    """
    try:
        items = Item.query.all()
        return jsonify(Items=[i.serialize_item for i in items])
    except Exception as e:
        return jsonify({"status": 500, "message": "Server error",
                        "error": e})


@item_blueprint.route("/catalog/api/v1/item/<int:itemId>/JSON")
@item_blueprint.route("/catalog/api/v1/item/<itemName>/JSON")
def getSingleItemJSON(itemId=None, itemName=""):
    """Get specific item details

        This API endpoint provides a GET method to query a specifc item in
        the database.
        The enpoint requires that a valid item id is passed or alternativetly
        the query can be done with the item name.
        If the item name is provided in the url, the query will be performed
        with the like operator, therefore the name (parameter) should not
        necessary be exactly the same as the one stored in the database.
        This route doesn't require any authentication.
        The endpoint returns a single object with the following keys:
            category_id,
            category_name,
            description,
            id (of the item),
            name,
            picture,
            user_id (creator of the item)

        In case of error an object is returned with the following keys:
            status (error code),
            error (error message)
    """
    try:
        if itemId:
            item = Item.query.filter_by(id=itemId).first()
        elif itemName:
            item = Item.query.filter(Item.name.like(itemName)).first()
        if item:
            return jsonify(item.serialize_item)
        else:
            return jsonify({"status": 404, "message": "No item found"})
    except Exception as e:
        return jsonify({"status": 500, "message": "Server error",
                        "error": e})


@item_blueprint.route("/catalog/api/v1/items/<categoryName>/JSON")
def getCategoryItemsJSON(categoryName):
    """Get all the items in a specific category

        This API endpoint provides a GET method to query a all the items in
        a specifc category.
        The enpoint requires that a valid category name is provided as
        parameter.
        The category name provided should exactly match the one stored in the
        database.
        This route doesn't require any authentication.
        The endpoint returns a single object with the following keys:
            category_id,
            category_name,
            description,
            id (of the item),
            name,
            picture,
            user_id (creator of the item)

        In case of error an object is returned with the following keys:
            status (error code),
            error (error message)
    """
    try:
        items = Item.query.filter_by(category_name=categoryName).all()
        return jsonify(Items=[i.serialize_item for i in items])
    except Exception as e:
        return jsonify({"status": 500, "message": "Server error",
                        "error": e})


@item_blueprint.route("/catalog/<categoryName>/new", methods=['GET', 'POST'])
@login_required
def addCategoryItem(categoryName):
    try:
        category = Category.query.filter_by(name=categoryName).first()
        if current_user.id == category.user_id or current_user.admin:
            if request.method == 'GET':
                return render_template('new_item.html', category=category,
                                       user=current_user)
            elif request.method == 'POST':
                if (request.form['name'] and request.form['picture'] and
                        request.form['description']):
                    newItem = Item(
                        name=request.form['name'],
                        picture=request.form['picture'],
                        description=request.form['description'],
                        category_id=category.id,
                        category_name=category.name,
                        user_id=current_user.id
                        )
                    db.session.add(newItem)
                    db.session.commit()
                    flash({
                        "message": "New item successfully created.",
                        "role": "success"
                        })
                    return redirect(url_for('main.showHome'))
                else:
                    flash({
                        "message": "Please fill in all the fields!",
                        "role": "failure"
                        })
                    return render_template('new_item.html', category=category,
                                           user=current_user)
        else:
            return handleUnauthorized()
    except exc.SQLAlchemyError as e:
        flash({
            "message":
                "No category found. Please add a category before" +
                " adding items.",
            "role": "failure"
            })
        return redirect(url_for('main.showHome'))


@item_blueprint.route("/catalog/<categoryName>/<itemName>")
def getItem(categoryName, itemName):
    try:
        item = Item.query.filter(Item.name == itemName,
                                 Item.category_name == categoryName).first()
        return jsonify(item.serialize_item)
    except exc.SQLAlchemyError as e:
        return jsonify({
            "message":
                "No item was found. Please retry.",
            "role": "failure"
            })
    except Exception as e:
        return redirect(url_for('main.showHome'))


@item_blueprint.route("/catalog/<categoryName>/<itemName>/edit",
                      methods=['GET', 'POST'])
@login_required
def editCategoryItem(categoryName, itemName):
    try:
        item = Item.query.filter(Item.name == itemName,
                                 Item.category_name == categoryName).first()
        if current_user.id == item.user_id or current_user.admin:
            if request.method == 'GET':
                return render_template('edit_item.html', item=item,
                                       user=current_user)
            elif request.method == 'POST':
                if (request.form['name'] and request.form['picture'] and
                        request.form['description']):
                    item.name = request.form['name']
                    item.picture = request.form['picture']
                    item.description = request.form['description']
                    item.user_id = current_user.id
                    db.session.add(item)
                    db.session.commit()
                    flash({
                        "message": "New item successfully added.",
                        "role": "success"
                         })
                    return redirect(url_for('main.showHome'))
                else:
                    flash({
                        "message": "Please fill up all the fields.",
                        "role": "failure"
                         })
                    return render_template('edit_item.html', item=item,
                                           user=current_user)

        else:
            return handleUnauthorized()
    except exc.SQLAlchemyError as e:
        flash({
            "message":
                "No item was found. Please retry.",
            "role": "failure"
            })
        return redirect(url_for('main.showHome'))


@item_blueprint.route("/catalog/<categoryName>/<itemName>/delete",
                      methods=['GET', 'POST'])
@login_required
def deleteCategoryItem(categoryName, itemName):
    try:
        item = Item.query.filter(Item.name == itemName,
                                 Item.category_name == categoryName).first()
        if current_user.id == item.user_id or current_user.admin:
            if request.method == 'GET':
                return jsonify({"name": item.name,
                                "category": item.category_name})
            elif request.method == 'POST':
                db.session.delete(item)
                db.session.commit()
                flash({
                    "message": "{} deleted.".format(item.name),
                    "role": "success"
                })
                return redirect(url_for('main.showHome'))
        else:
            return handleUnauthorized()
    except exc.SQLAlchemyError as e:
        flash({
            "message":
                "Something went wrong while processing your request.",
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
