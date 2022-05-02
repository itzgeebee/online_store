from functools import wraps
import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
# from forms import CreatePostForm, CreateUserForm, LoginUserForm, CommentForm
from flask_gravatar import Gravatar

login_manager = LoginManager()
app = Flask(__name__)
login_manager.init_app(app)
app.config['SECRET_KEY'] = "secretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(250), nullable=False)
    product_description = db.Column(db.String(2000), nullable=False)
    category = db.Column(db.String(250), nullable=False)
    # reviews = db.relationship("Review", back_populates="product_name")
    order = db.relationship("Order", back_populates="product_name")

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Customer(UserMixin, db.Model):
    __tablename__ = "customers"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(250), nullable=False)
    street = db.Column(db.String(250), nullable=False)
    city = db.Column(db.String(250), nullable=False)
    zip = db.Column(db.String(250), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    mail = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(500), nullable=False)
    # reviews = db.relationship("Review", back_populates="customer_name")
    order = db.relationship("Order", back_populates="customer_name")

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    order_name = db.relationship("Order", back_populates="review_comms")

    # product_name = db.relationship("Product", back_populates="reviews")
    # product_id = db.Column(db.Integer, db.ForeignKey('products.id'))

    review_comment = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    customer_name = db.relationship("Customer", back_populates="order")
    product_name = db.relationship("Product", back_populates="order")
    review_comms = db.relationship("Review", back_populates="order_name")

    to_street = db.Column(db.String(250), nullable=False)
    to_city = db.Column(db.String(250), nullable=False)
    to_zip = db.Column(db.String(250), nullable=False)
    zip = db.Column(db.String(250), nullable=False)
    ship_date = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/", methods=["GET", "POST"])
def home():
    all_products = Product.query.all()
    rez = []
    for i in all_products:
        result = i.to_dict()
        rez.append(result)

    products_json = jsonify(products=rez).json
    return products_json


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
