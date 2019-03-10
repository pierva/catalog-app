#catalog/main/views.py

from flask import render_template, Blueprint
from flask_login import current_user
from flask_login import login_required
from sqlalchemy import exc

from catalog.models import Category, Item



# Configuration
main_blueprint = Blueprint('main', __name__,)


# routes
@main_blueprint.route('/')
@main_blueprint.route('/catalog')
# @login_required
def showHome():
    # TODO: getUserInfo from login_session and send the user info to the template
    try:
        categories = Category.query.all()
        items = Item.query.order_by(Item.id.desc()).limit(7)
        return render_template('home.html',
            categories=categories, user=None, items=items)

    except exc.SQLAlchemyError as e:
        flash({
            "message": "Error while communicating with the db.\n\n" + e.message,
            "role": "failure"
             })
        return redirect('/')
