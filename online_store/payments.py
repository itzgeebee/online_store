from flask import (render_template,
                   redirect, url_for,
                   flash, request,
                   jsonify, session)
from online_store.models import (Product,
                                 Order, OrderDetails,
                                 )
from online_store import app, mail_sender, db
from flask_login import (login_required,
                         current_user)
from flask_mail import Message
from threading import Thread
from datetime import date
import stripe

stripe.api_key = app.config['STRIPE_SECRET_KEY']


def send_mail(app, msg):
    with app.app_context():
        mail_sender.send(msg)


@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    prod_id = session["product_ids"]
    prod_qty = session["quantities"]
    items_to_buy = []
    for i in range(len(prod_id)):
        product_to_buy = Product.query.get(prod_id[i])
        qty = int(prod_qty[i])
        qty_left = product_to_buy.quantity
        if qty > qty_left:
            error = f"Sorry we only have {qty_left} quantity left"
            return redirect(url_for("cart", error=error))
        else:
            line_dict = {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product_to_buy.product_description,
                    },
                    'unit_amount': (product_to_buy.price // 550) * 100,
                },
                'quantity': qty,
            }
            items_to_buy.append(line_dict)

    strt = request.form.get("strt")
    cty = request.form.get("city")
    to_zip = request.form.get("zip")

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=items_to_buy,
            mode='payment',
            success_url=url_for("success",
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
    id_list = session["product_ids"]
    qty_list = session["quantities"]

    customer_order = OrderDetails(
        customer_name=current_user,
        to_street=request.args.get("strt"),
        to_city=request.args.get("cty"),
        zip=request.args.get("zip"),
        order_date=date.today()
    )

    db.session.add(customer_order)

    for i in range(len(id_list)):
        prod = Product.query.get(id_list[i])
        prod.quantity -= int(qty_list[i])
        order = Order(
            product_name=prod,
            quantity=int(qty_list[i]),
            order_name=customer_order
        )
        db.session.add(order)

    db.session.commit()

    mesg = "Transaction Successful. Thanks for patronizing"

    # template = f"<html>" \
    #            f"<h2>Receipt</h2>\n <p>Your receipt from Laptohaven</p> \n" \
    #            f"<ul><li>Product: {prod.product_description}</li>" \
    #            f"<li>Price: {prod.price}</li>" \
    #            f"<li>Price:Quantity: {qty}</li>" \
    #            f"<li>Date: {date.today().strftime('%d %b, %Y')}</li>" \
    #            f"</ul>" \
    #            f"</html>"

    msg = Message()
    msg.subject = "Receipt from laptohaven"
    msg.recipients = [current_user.mail]
    msg.body = 'Thanks for your patronage, do come again'
    # msg.html = template
    Thread(target=send_mail, args=(app, msg)).start()
    session.pop("product_ids")
    session.pop("quantities")

    app.logger.info('Info level log')
    app.logger.warning('Warning level log')
    app.logger.error('Error level log')
    app.logger.critical('Critical level log')
    return render_template("feedback.html", txt=mesg)

