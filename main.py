from functools import wraps
import os
from time import time

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
from flask_mail import Mail, Message
from threading import Thread
from itsdangerous import TimedSerializer as serializer
import jwt


login_manager = LoginManager()
app = Flask(__name__)
login_manager.init_app(app)
app.config['SECRET_KEY'] = os.urandom(10)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv("EMAIL")
app.config['MAIL_PASSWORD'] = os.environ.get("EMAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = "noreply@laptohaven.com"
db = SQLAlchemy(app)
mail_sender = Mail(app)


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(250), nullable=False)
    product_description = db.Column(db.String(2000), nullable=False)
    category = db.Column(db.String(250), nullable=False)
    price = db.Column(db.String(250), nullable=False)
    # pic_data = db.Column(db.LargeBinary, nullable=False)  # Actual data, needed for Download
    img_url = db.Column(db.String(500), nullable=False)  # Data to render the pic in browser
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
    mail = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(500), nullable=False)
    # reviews = db.relationship("Review", back_populates="customer_name")
    order = db.relationship("Order", back_populates="customer_name")

    def get_token(self, expires_sec=300):
        return jwt.encode({'reset_password': self.mail,
                           'exp': time() + expires_sec},
                            key=app.config['SECRET_KEY'])

    @staticmethod
    def verify_token(token):
        try:
            user = jwt.decode(token,algorithms="HS256",
                              key=app.config["SECRET_KEY"])['reset_password']
        except Exception as e:
            print(e)
            return None
        return Customer.query.filter_by(mail=user).first()


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


def send_email(user):

    tok = user.get_token()
    msg = Message()
    msg.subject = "reset password"
    msg.recipients = [user.mail]
    msg.body = f"follow this link to reset your password {tok}"
    mail_sender.send(msg)


@login_manager.user_loader
def load_user(id):
    return Customer.query.get(id)


@app.route("/", methods=["GET", "POST"])
def home():
    all_products = Product.query.all()
    rez = []
    for i in all_products:
        result = i.to_dict()
        rez.append(result)

    products_json = jsonify(products=rez).json
    return products_json


@app.route("/product", methods=["GET", "POST"])
def product():

    product_id = request.args.get("id")
    specific_product = Product.query.get(product_id)
    if specific_product:
        # print(specific_product.to_dict())
        products_json = jsonify(product=specific_product.to_dict()).json
        return products_json
    else:
        return jsonify({"error": "not found"}), 404


@app.route("/search", methods=["POST"])
def search():
    product_id = request.form.get("product")
    query_result = db.session.query(Product).filter(
        Product.product_name.like(f"{product_id}%") | Product.product_description.like(f"{product_id}%")
        | Product.category.like(f"{product_id}%")
    )
    if query_result:
        result_list = []
        for i in query_result:
            rez = i.to_dict()
            result_list.append(rez)
        products_json = jsonify(product=result_list).json
        return products_json
    else:
        return jsonify({"error": "not found"}), 404

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full-name")
        street = request.form.get("street")
        city = request.form.get("city")
        zip = request.form.get("zip")
        phone = request.form.get("phone")
        mail = request.form.get("mail")
        password = request.form.get("password")

        new_user = Customer(mail=mail,
                        password=generate_password_hash(password, method='pbkdf2'
                                                                         ':sha256',
                                                        salt_length=8),
                        full_name=full_name,
                        street=street,
                        city=city,
                        zip=zip,
                        phone=phone
                        )
        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            error = "email already exists"
            return jsonify(error=error).json
        else:
            login_user(new_user, remember=True)
            return jsonify({"message": "Success"}).json


customer = Customer.query.get(1)
print("my name is ", customer.mail)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_email = request.form.get("mail")
        user_password = request.form.get("password")
        user = Customer.query.filter_by(mail=user_email).first()
        if not user:
            return jsonify({"error": "email not found"}).json
        else:
            if check_password_hash(pwhash=user.password, password=user_password):
                login_user(user, remember=True)
                return jsonify({"message": "success"}).json
            else:
                return jsonify({"error": "invalid password"}).json


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        mail = request.form.get("mail")
        user = Customer.query.filter_by(mail=mail).first()
        if not user:
            return jsonify({"error": "email not found"}).json
        else:
            send_email(user)
            # Thread(target=send_email, args=(app, msg)).start()
            return jsonify({"message": "success"}).json

            # with mail_sender.record_messages() as outbox:
            #
            #     mail_sender.send_message(subject='testing',
            #                       body='test',
            #                       recipients=emails)
            #
            #     assert len(outbox) == 1
            #     assert outbox[0].subject == "testing"


@login_required
@app.route("/reset-password", methods=["GET", "POST", "PUT"])
def password_reset():
    if request.method == "POST":
        mail = request.form.get("mail")
        old_password = request.form.get("old-password")
        new_password = request.form.get("new-password")
        confirm_password = request.form.get("confirm-password")
        print(confirm_password)
        user = Customer.query.filter_by(mail=mail).first()
        if check_password_hash(pwhash=user.password, password=old_password):
            if new_password == confirm_password:
                user.password = generate_password_hash(new_password, method='pbkdf2'
                                                                         ':sha256',
                                                        salt_length=8)
                db.session.commit()
                return jsonify({"message": "Success"})
            else:
                return jsonify({"error": "passwords do not match"}), 404

        else:
            return jsonify({"error": "invalid old password"}), 404

        # if new_password == confirm_password:

@app.route("/reset-password/<token>", methods=["GET", "POST", "PUT"])
def verify_reset(token):
    user = Customer.verify_token(token)
    if user is None:
        return jsonify({"error": "invalid or expired token"}), 404
    print(user)
    return jsonify({"message": "Success"})








if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
