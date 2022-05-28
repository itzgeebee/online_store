from flask import (render_template,
                   redirect, url_for,
                   flash, request,
                   jsonify)
from online_store.models import (Customer, Product,
                                 Order, OrderDetails,
                                 )
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash, check_password_hash
from online_store import app, db,mail_sender, login_manager
from flask_login import (login_user, login_required,
                         current_user, logout_user)
from sqlalchemy.exc import IntegrityError
from online_store.forms import (ChangePassword, CreateUserForm,
                                LoginUserForm, ResetPassword,
                                EditUserForm)
from flask_mail import Message


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


@app.route("/register", methods=["GET", "POST"])
def register():
    error = request.args.get("error")
    prev_page = request.args.get("prev_page")
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

                app.logger.error('Error level log')
                app.logger.critical('Critical level log')
                db.session.rollback()
                return redirect(url_for('login', error=error))
            else:
                login_user(new_user, remember=True)
                if prev_page:
                    return redirect(url_for('cart'))
                return redirect(url_for('home'))
        else:

            app.logger.error('Error level log')
            app.logger.critical('Critical level log')
            error = "confirm password doesn't match password"
            return redirect(url_for("register", error=error))
    return render_template("register.html", form=reg_form,
                           logged_in=current_user.is_authenticated,
                           error=error)


@app.route('/login', methods=["GET", "POST"])
def login():
    error = request.args.get("error")
    login_form = LoginUserForm()
    prev_page = request.args.get("prev_page")
    if login_form.validate_on_submit():
        user_email = login_form.email.data
        user_password = login_form.password.data
        user = Customer.query.filter_by(mail=user_email).first()
        if not user:
            app.logger.error('Error level log')
            app.logger.critical('Critical level log')
            return redirect(url_for("login", error="Invalid email, try signing up"))
        else:
            if check_password_hash(pwhash=user.password, password=user_password):
                login_user(user, remember=True)
                if prev_page:
                    return redirect(url_for('cart'))
                return redirect(url_for('home', name=user.first_name))
            else:
                return redirect(url_for("login", error="Invalid password"))
    return render_template("login.html", form=login_form,
                           logged_in=current_user.is_authenticated,
                           error=error)


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
    error = request.args.get("error")
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
                app.logger.error('Error level log')
                app.logger.critical('Critical level log')
                error = "Invalid old password"
                db.session.rollback()
                return redirect(url_for("password_reset", error=error))

        else:

            app.logger.error('Error level log')
            app.logger.critical('Critical level log')
            error = "confirm password does not match new password"
            return redirect(url_for("password_reset", error=error))

    return render_template('edit.html', form=np_form,
                           logged_in=current_user.is_authenticated,
                           error=error)


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def verify_reset(token):
    error = request.args.get("error")
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

            app.logger.error('Error level log')
            app.logger.critical('Critical level log')
            return redirect(url_for("verify_reset", error="passwords do not match"))

    app.logger.error('Error level log')
    app.logger.critical('Critical level log')
    return render_template("edit.html", form=reset_form,
                           logged_in=current_user.is_authenticated,
                           error=error)


@app.route('/account')
@login_required
def account():
    user_id = request.args.get("user_id")
    customer = Customer.query.get(user_id)
    order_table = db.session.query(OrderDetails,
                                   Order, Product).select_from(
        OrderDetails).join(Order).join(Product).with_entities(OrderDetails.order_date,
                                                              Product.price,
                                                              Product.product_description,
                                                              Order.quantity).filter(
        OrderDetails.customer_id == user_id
    ).all()

    app.logger.error('Error level log')
    app.logger.critical('Critical level log')
    return render_template("accounts.html", user=customer,
                           logged_in=current_user.is_authenticated,
                           user_order=order_table)


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


        app.logger.error('Error level log')
        app.logger.critical('Critical level log')
        return redirect(url_for("account", user_id=user_id,
                                message="Profile update successful"))


    app.logger.error('Error level log')
    app.logger.critical('Critical level log')
    return render_template("edit.html", form=eu_form,
                           logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))
