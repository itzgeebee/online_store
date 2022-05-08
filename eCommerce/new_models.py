from flask_login import UserMixin
from eCommerce import db
from eCommerce import app
import jwt
from sqlalchemy.orm import relationship
from time import time


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
