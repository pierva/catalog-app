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

@app.route("/")
@app.route("/catalog")
def showHome():
    return 'Home page'


@app.route("/catalog/new")
def addCategory():
    return 'Add a new category'


@app.route("/catalog/<categoryName>/edit")
def editCategory(categoryName):
    return 'Edit {}'.format(categoryName)


@app.route("/catalog/<categoryName>/delete")
def deleteCategory(categoryName):
    return 'Delete {}'.format(categoryName)


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
