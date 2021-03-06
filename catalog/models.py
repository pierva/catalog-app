import random
import string
import datetime

from catalog import db, bcrypt


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, index=True, unique=True)
    username = db.Column(db.String, nullable=True)
    password = db.Column(db.String(64), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    categories = db.relationship("Category", lazy=True, back_populates='user')

    def __init__(self, email, password, admin, username=""):
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.registered_on = datetime.datetime.now()
        self.admin = admin
        self.username = username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<email {}'.format(self.email)


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User", back_populates='categories',
                           cascade="save-update")
    items = db.relationship('Item', back_populates='category',
                            cascade="all, delete")

    @property
    def serialize_category(self):
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id
        }

class Item(db.Model):
    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(50), nullable=False)
    picture = db.Column(db.String, nullable=True)
    description = db.Column(db.String)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'),
                            nullable=False)
    category_name = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                        nullable=False)
    category = db.relationship("Category", foreign_keys=[category_id],
                               back_populates="items", cascade="all, delete")
    db.relationship("User")


    @property
    def serialize_item(self):
        return {
            'id': self.id,
            'name': self.name,
            'picture': self.picture,
            'user_id': self.user_id,
            'description': self.description,
            'category_id': self.category_id,
            'category_name': self.category_name,
        }
