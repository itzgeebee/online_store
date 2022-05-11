from flask_login import UserMixin
from online_store import db, app, migrate
import jwt
from sqlalchemy.orm import relationship
from time import time


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(250), nullable=False)
    product_description = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(30), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    # pic_data = db.Column(db.LargeBinary, nullable=False)  # Actual data, needed for Download
    img_url = db.Column(db.String(500), nullable=False)  # Data to render the pic in browser
    # reviews = db.relationship("Review", back_populates="product_name")
    order = db.relationship("Order", back_populates="product_name")

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Customer(UserMixin, db.Model):
    __tablename__ = "customers"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    street = db.Column(db.String(250), nullable=False)
    city = db.Column(db.String(250), nullable=False)
    zip = db.Column(db.String(250), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    mail = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(500), nullable=False)
    # reviews = db.relationship("Review", back_populates="customer_name")
    order = db.relationship("Order", back_populates="customer_name", cascade="all, delete")

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


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    customer_name = db.relationship("Customer", back_populates="order")
    product_name = db.relationship("Product", back_populates="order")

    quantity = db.Column(db.Integer, nullable=False)
    to_street = db.Column(db.String(250), nullable=False)
    to_city = db.Column(db.String(250), nullable=False)
    zip = db.Column(db.String(250), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
# db.drop_all()
# db.create_all()