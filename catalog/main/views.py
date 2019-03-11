#catalog/main/views.py

from flask import render_template, Blueprint, flash, abort
from flask_login import current_user
from flask_login import login_required
from sqlalchemy import exc

from catalog.models import Category, Item
from flask_login import current_user



# Configuration
main_blueprint = Blueprint('main', __name__,)


# routes
@main_blueprint.route('/')
@main_blueprint.route('/catalog')
def showHome():
    try:
        categories = Category.query.all()
        items = Item.query.order_by(Item.id.desc()).limit(7)
        return render_template('home.html',
            categories=categories, user=current_user, items=items)

    except exc.SQLAlchemyError as e:
        flash({
            "message": "Error while communicating with the db.\n\n" + str(e),
            "role": "failure"
             })
        return abort(500)
