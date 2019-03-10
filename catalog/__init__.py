import os
import requests
from flask import (Flask, request, url_for, flash, render_template,
    redirect, jsonify, abort)


from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# routes setup
from catalog.main.views import main_blueprint
from catalog.user.views import user_blueprint
from catalog.category.views import category_blueprint
from catalog.item.views import item_blueprint
app.register_blueprint(main_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(category_blueprint)
app.register_blueprint(item_blueprint)

from catalog.models import User



# error handlers setup (use with abort(errCode))
@app.errorhandler(403)
def forbidden_page(error):
    return render_template("errors/403.html"), 403


@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error_page(error):
    return render_template("errors/500.html"), 500
