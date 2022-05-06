from flask import render_template, redirect, url_for, flash, request, jsonify
from eCommerce.models import Customer, Product, Order, Review
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash, check_password_hash
from eCommerce import app, mail_sender, login_manager
from flask_login import login_user, login_required, current_user, logout_user
from flask_mail import Message
from sqlalchemy.exc import IntegrityError
from eCommerce import db
from threading import Thread
from datetime import date
import stripe

stripe.api_key = app.config['STRIPE_SECRET_KEY']


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



@app.route("/reset-password", methods=["GET", "POST", "PUT"])
@login_required
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



@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():


    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[{
                              'price_data': {
                                'currency': 'usd',
                                'product_data': {
                                  'name': 'T-shirt',
                                },
                                'unit_amount': 20000,
                              },
                              'quantity': 1,
                        }],
            mode='payment',
            success_url=url_for("success", _external=True),
            cancel_url=url_for("cancel", _external=True),
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)


@app.route("/cancel")
def cancel():
    return jsonify({"error": "Something wrong with payment"})


@app.route("/success", methods=["POST"])
def success():
    order = Order()
    order.customer_name = current_user.name

    user_bought = [
        {
            "id": 3,
            "qty": 2,

        }
    ]
    for i in user_bought:
        product_bought = Product.query.get(i["id"])
        product_bought.quantity = product_bought.quantity - i["qty"]
        db.session.commit()

    return jsonify({"error": "Something wrong with payment"})








