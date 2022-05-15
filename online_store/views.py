from flask import render_template, redirect, url_for, flash, request, jsonify, session
from online_store.models import Customer, Product, Order
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash, check_password_hash
from online_store import app, mail_sender, login_manager
from flask_login import login_user, login_required, current_user, logout_user
from flask_mail import Message
from sqlalchemy.exc import IntegrityError
from online_store import db
from threading import Thread
from datetime import date
import stripe
from online_store.forms import ChangePassword, CreateUserForm, LoginUserForm, ResetPassword, EditUserForm

stripe.api_key = app.config['STRIPE_SECRET_KEY']


def send_mail(app, msg):
    with app.app_context():
        mail_sender.send(msg)


def send_email(user):
    tok = user.get_token()
    msg = Message()
    msg.subject = "reset password"
    msg.recipients = [user.mail]
    msg.body = f"follow this link to reset your password " \
               f"{url_for('verify_reset', token=tok)}"
    mail_sender.send(msg)


@login_manager.user_loader
def load_user(id):
    return Customer.query.get(id)


@app.route("/", methods=["GET", "POST"])
def home():
    # session.pop("search")
    page = request.args.get("page", 1, type=int)
    all_prods = Product.query.paginate(per_page=64, page=page)

    prod_list = []
    for i in all_prods.items:
        prod = i.to_dict()
        prod_list.append(prod)
    page_url = 'home'
    return render_template("index.html", prods=prod_list, pages=all_prods,
                           logged_in=current_user.is_authenticated, page_url=page_url
                           )


@app.route("/product", methods=["GET", "POST"])
def product():
    product_id = request.args.get("id")
    specific_product = Product.query.get(product_id)
    if specific_product:
        prod = specific_product.to_dict()
        return render_template("product.html", prod=prod, logged_in=current_user.is_authenticated)


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        product_id = request.form.get("product")
        session['search'] = product_id
    else:
        if "search" in session:
            product_id = session.get("search")

    page = request.args.get("page", 1, type=int)
    query_result = db.session.query(Product).filter(
        Product.product_name.like(f"{product_id}%") | Product.product_description.like(f"{product_id}%")
        | Product.category.like(f"{product_id}%")).paginate(per_page=40, page=page)

    if query_result:
        result_list = []
        for i in query_result.items:
            rez = i.to_dict()
            result_list.append(rez)
        page_url = "search"
    else:
        error = "Nothing found"
        return redirect(url_for("home", error=error))
    return render_template("index.html", prods=result_list, pages=query_result,
                           logged_in=current_user.is_authenticated, page_url=page_url
                           )


@app.route("/filter", methods=["GET", "POST"])
def filter():
    if request.method == "POST":
        min_price = request.form.get("min")
        max_price = request.form.get("max")
        category = request.form.get("flexRadioDefault")
        session["min"] = min_price
        session["max"] = max_price
        session["category"] = category

    else:
        if "min" in session:
            min_price = session["min"]
            max_price = session["max"]
            category = session["category"]

    page = request.args.get("page", 1, type=int)
    filter_result = Product.query.filter(
        Product.price > min_price,
        Product.price < max_price,
        Product.category == category).paginate(per_page=56, page=page)
    if filter_result:
        result_list = []
        for i in filter_result.items:
            rez = i.to_dict()
            result_list.append(rez)
        page_url = 'filter'
        return render_template("index.html", prods=result_list, pages=filter_result,
                               logged_in=current_user.is_authenticated, page_url=page_url
                               )
    else:
        error = "Nothing found"
        return redirect(url_for("home", error=error))


@app.route("/register", methods=["GET", "POST"])
def register():
    prod = request.args.get("prod")
    reg_form = CreateUserForm()
    if reg_form.validate_on_submit():
        first_name = reg_form.first_name.data
        last_name = reg_form.last_name.data
        street = reg_form.street.data
        city = reg_form.city.data
        zip = reg_form.zip.data
        phone = reg_form.phone.data
        mail = reg_form.email.data
        password = reg_form.password.data
        confirm_password = reg_form.confirm_password.data
        if password == confirm_password:
            new_user = Customer(mail=mail,
                                password=generate_password_hash(password, method='pbkdf2'
                                                                                 ':sha256',
                                                                salt_length=8),
                                first_name=first_name,
                                last_name=last_name,
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
                return redirect(url_for('login', error=error))
            else:
                login_user(new_user, remember=True)
                if prod:
                    return redirect(url_for('product', id=prod))
                return redirect(url_for('home'))
        else:
            error = "confirm password doesn't match password"
            return redirect(url_for("register", error=error))
    return render_template("register.html", form=reg_form, logged_in=current_user.is_authenticated)


@app.route('/login', methods=["GET", "POST"])
def login():
    login_form = LoginUserForm()
    prod = request.args.get("prod")
    if login_form.validate_on_submit():
        user_email = login_form.email.data
        user_password = login_form.password.data
        user = Customer.query.filter_by(mail=user_email).first()
        if not user:
            return redirect(url_for("login", error="Invalid email, try signing up"))
        else:
            if check_password_hash(pwhash=user.password, password=user_password):
                login_user(user, remember=True)
                if prod:
                    return redirect(url_for('product', id=prod))
                return redirect(url_for('home', name=user.first_name))
            else:
                return redirect(url_for("login", error="Invalid password"))
    return render_template("login.html", form=login_form, logged_in=current_user.is_authenticated)


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        mail = request.form.get("mail")
        user = Customer.query.filter_by(mail=mail).first()
        if not user:
            return redirect(url_for('forgot_password', error="email not found"))
        else:
            send_email(user)
            mesg = "Check your email for link to change password"
            return render_template("feedback.html", txt=mesg)

    return render_template("forgot-password.html")


@app.route("/reset-password", methods=["GET", "POST", "PUT"])
@login_required
def password_reset():
    user_id = request.args.get("user_id")
    np_form = ChangePassword()
    if np_form.validate_on_submit():
        old_password = np_form.old_password.data
        new_password = np_form.new_password.data
        confirm_password = np_form.confirm_password.data
        if new_password == confirm_password:
            user = Customer.query.get(user_id)
            if check_password_hash(pwhash=user.password, password=old_password):
                user.password = generate_password_hash(new_password, method='pbkdf2'
                                                                            ':sha256',
                                                       salt_length=8)
                db.session.commit()
                return redirect(url_for('account', user_id=user_id,
                                        message="Password changed"))
            else:
                error = "Invalid old password"
                return redirect(url_for("password_reset", error=error))
        else:
            error = "confirm password does not match new password"
            return redirect(url_for("password_reset", error=error))
    return render_template('edit.html', form=np_form,
                           logged_in=current_user.is_authenticated)


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def verify_reset(token):
    reset_form = ResetPassword()
    user = Customer.verify_token(token)
    if user is None:
        return jsonify({"error": "invalid or expired token"}), 404
    if reset_form.validate_on_submit():
        new_password = reset_form.new_password.data
        confirm_password = reset_form.confirm_password.data
        if new_password == confirm_password:
            user.password = generate_password_hash(new_password,
                                                   method='pbkdf2'
                                                          ':sha256',
                                                   salt_length=8)
            db.session.commit()
            login_user(user)
            return redirect(url_for('home'))
        else:
            return redirect(url_for("verify_reset", error="passwords do not match"))
    return render_template("edit.html", form=reset_form,
                           logged_in=current_user.is_authenticated)


@app.route('/account')
@login_required
def account():
    user_id = request.args.get("user_id")
    customer = Customer.query.get(user_id)

    return render_template("accounts.html", user=customer,
                           logged_in=current_user.is_authenticated)


@app.route('/edit-profile', methods=["GET", "POST"])
@login_required
def edit_profile():
    user_id = request.args.get("user_id")
    user = Customer.query.get(user_id)
    eu_form = EditUserForm(
        email=user.mail,
        first_name=user.first_name,
        last_name=user.last_name,
        street=user.street,
        city=user.city,
        zip=user.zip,
        phone=user.phone
    )
    if eu_form.validate_on_submit():
        user.mail = eu_form.email.data
        user.first_name = eu_form.first_name.data
        user.last_name = eu_form.last_name.data
        user.street = eu_form.street.data
        user.city = eu_form.city.data
        user.zip = eu_form.zip.data
        user.phone = eu_form.phone.data
        db.session.commit()
        return redirect(url_for("account", user_id=user_id,
                                message="Profile update successful"))
    return render_template("edit.html", form=eu_form,
                           logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    prod_id = request.form.get("prod_id")
    qty = int(request.form.get("qty"))
    if qty < 1:
        error = "quantity should not be less than 1"
        return redirect(url_for("product", id=prod_id, error=error))
    strt = request.form.get("strt")
    cty = request.form.get("city")
    to_zip = request.form.get("zip")
    product_to_buy = Product.query.get(prod_id)
    qty_left = product_to_buy.quantity
    if qty > qty_left:
        print(qty_left)
        error = f"Sorry we only have {qty_left} quantity left"
        return redirect(url_for("product", id=prod_id, error=error))

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product_to_buy.product_description,
                    },
                    'unit_amount': product_to_buy.price,
                },
                'quantity': qty,
            }],
            mode='payment',
            success_url=url_for("success",
                                prod_id=prod_id,
                                qty=qty,
                                strt=strt,
                                cty=cty,
                                zip=to_zip,
                                _external=True),
            cancel_url=url_for("cancel", _external=True),
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)


@app.route("/cancel")
def cancel():
    mesg = "Transaction failed, please check your payment details and try again"
    return render_template("feedback.html", txt=mesg)


@app.route("/success", methods=["GET", "POST"])
@login_required
def success():
    prod_id = int(request.args.get("prod_id"))
    prod = Product.query.get(prod_id)
    qty = request.args.get("qty")
    strt = request.args.get("strt")
    cty = request.args.get("cty")
    to_zip = request.args.get("zip")
    order = Order(
        customer_name=current_user,
        product_name=prod,
        quantity=qty,
        to_street=strt,
        to_city=cty,
        zip=to_zip,
        order_date=date.today()
    )
    prod.quantity -= int(qty)
    db.session.add(order)
    db.session.commit()
    mesg = "Transaction Successful. Thanks for patronizing"
    template = f"<html>" \
               f"<h2>Receipt</h2>\n <p>Your receipt from Laptohaven</p> \n" \
               f"<ul><li>Product: {prod.product_description}</li>" \
               f"<li>Price: {prod.price}</li>" \
               f"<li>Price:Quantity: {qty}</li>" \
               f"<li>Date: {date.today().strftime('%d %b, %Y')}</li>" \
               f"</ul>" \
               f"</html>"

    msg = Message()
    msg.subject = "Receipt from laptohaven"
    msg.recipients = [current_user.mail]
    msg.body = 'Thanks for your patronage, do come again'
    msg.html = template
    Thread(target=send_mail, args=(app, msg)).start()
    return render_template("feedback.html", txt=mesg)
