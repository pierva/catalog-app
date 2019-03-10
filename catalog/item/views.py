# catalog/item/views.py

from flask import render_template, Blueprint, request, flash, redirect, url_for, jsonify
from catalog.models import Category, Item
from sqlalchemy import exc
from catalog import db

item_blueprint = Blueprint('item', __name__,)

@item_blueprint.route("/catalog/<categoryName>")
@item_blueprint.route("/catalog/<categoryName>/items")
def getCategoryItems(categoryName):
    try:
        items = Item.query.filter_by(category_name=categoryName).all()
        return render_template("partials/items-list.html", items=items)

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


@item_blueprint.route("/catalog/<categoryName>/new", methods=['GET', 'POST'])
def addCategoryItem(categoryName):
    try:
        category = Category.query.filter_by(name = categoryName).one()
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
            db.session.add(newItem)
            db.session.commit()
            flash({
                "message": "New item successfully created.",
                "role": "success"
            })
            return redirect(url_for('main.showHome'))
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
            Item.category_name == categoryName).one()
        return jsonify(item.serialize_item)
    except exc.SQLAlchemyError as e:
        return jsonify({
            "message":
                "No item was found. Please retry.",
            "role": "failure"
            })
    except Exception as e:
        return redirect(url_for('main.showHome'))


@item_blueprint.route("/catalog/<categoryName>/<itemName>/edit", methods=['GET', 'POST'])
def editCategoryItem(categoryName, itemName):
    try:
        item = Item.query.filter(Item.name == itemName,
            Item.category_name == categoryName).one()
        if request.method == 'GET':
            return render_template('edit_item.html', item=item)
        elif request.method == 'POST':
            item.name = request.form['name']
            item.picture = request.form['picture']
            item.description = request.form['description']
            db.session.add(item)
            db.session.commit()
            return redirect(url_for('main.showHome'))
    except exc.SQLAlchemyError as e:
        flash({
            "message":
                "No item was found. Please retry.",
            "role": "failure"
            })
        return redirect(url_for('main.showHome'))


@item_blueprint.route("/catalog/<categoryName>/<itemName>/delete", methods=['GET', 'POST'])
def deleteCategoryItem(categoryName, itemName):
    try:
        item = Item.query.filter(Item.name == itemName,
            Item.category_name == categoryName).one()
        if request.method == 'GET':
            return jsonify({"name": item.name, "category": item.category_name})
        elif request.method == 'POST':
            db.session.delete(item)
            db.session.commit()
            flash({
                "message": "{} deleted.".format(item.name),
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
        return redirect(url_for('main.showHome'))
