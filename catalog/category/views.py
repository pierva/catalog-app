# catalog/category/views.py
from flask import render_template, Blueprint, request, flash, redirect, url_for, jsonify
from catalog.models import Category, Item
from sqlalchemy import exc
from catalog import db


category_blueprint = Blueprint('category', __name__,)

@category_blueprint.route("/catalog/new", methods=['GET', 'POST'])
def newCategory():
    if request.method == 'GET':
        return render_template('new_category.html')
    elif request.method == 'POST':
        try:
            newCategory = Category(name = request.form['name'])
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
def editCategory(id):
    try:
        category = Category.query.filter_by(id=id).one()
        if request.method == 'POST':
            category.name = request.form['name']
            db.session.add(category)
            db.session.commit()
            flash({
                "message": "Category successfully updated!",
                "role": "success"
                 })
            return redirect(url_for('main.showHome'))
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


@category_blueprint.route("/catalog/<int:id>/delete", methods=['GET', 'POST'])
def deleteCategory(id):
    try:
        category = Category.query.filter_by(id=id).first()
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
    except exc.SQLAlchemyError as e:
        flash({
            "message": "No category was found.",
            "role": "failure"
             })
        return redirect(url_for('main.showHome'))
