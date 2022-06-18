import sys
from flask import (render_template,
                   redirect, url_for,
                   flash, request,
                   jsonify, session)
from online_store.models import (Product,
                                 Reviews)
from werkzeug.exceptions import abort
from online_store import app, db
from flask_login import (login_required,
                         current_user)


@app.route("/add-to-cart", methods=['GET', 'POST'])
def add_to_cart():
    error = False

    if request.method == "POST":
        try:
            product_id = request.get_json()["prod_id"]
            quantity = request.get_json()["qty"]

            if "product_ids" not in session:
                session["product_ids"] = []
                session["quantities"] = []
            id_list = session["product_ids"]
            id_list.append(product_id)
            qty_list = session["quantities"]
            qty_list.append(quantity)
            session["product_ids"] = id_list
            session["quantities"] = qty_list
        except:
            error = True
            print(sys.exc_info())
        if error:
            app.logger.error('Error level log')
            app.logger.critical('Critical level log')
            abort(400)

        return jsonify({"message": "Product added to cart"})


@app.route('/cart')
def cart():
    try:
        prod_ids = session["product_ids"]
    except KeyError:
        return redirect(url_for('home', message="No item in cart yet, start shopping"))
    if prod_ids == []:
        return redirect(url_for("home", message="Empty cart, start shopping"))
    prod_qty = session["quantities"]
    cart_prods = []
    calculator_list = []
    for i in range(len(prod_ids)):
        prd = Product.query.get(prod_ids[i])
        qty = int(prod_qty[i])
        cart_product = {"prod": prd, "qty": qty}
        price = prd.price * qty
        calculator_list.append(price)
        cart_prods.append(cart_product)
    total = sum(calculator_list)

    app.logger.info('Info level log')
    app.logger.warning('Warning level log')
    app.logger.error('Error level log')
    app.logger.critical('Critical level log')
    return render_template("checkout.html", prods=cart_prods,
                           total=total, logged_in=current_user.is_authenticated)


@app.route("/remove-from-cart/<int:prodId>", methods=["DELETE"])
def remove_from_cart(prodId):
    prod = prodId
    temp_id_list = session["product_ids"]
    temp_qty = session["quantities"]
    temp_id_list.pop(prod)
    temp_qty.pop(prod)
    session["product_ids"] = temp_id_list
    session["quantities"] = temp_qty

    app.logger.info('Info level log')
    app.logger.warning('Warning level log')
    app.logger.error('Error level log')
    app.logger.critical('Critical level log')
    return jsonify({
        "success": True
    })


@app.route("/add-rating/<prodId>", methods=["POST"])
@login_required
def add_rating(prodId):
    prod = Product.query.get(prodId)
    error = False
    try:
        rating = request.get_json()["rate"]
        review = request.get_json()["rev"]
        new_review = Reviews(
            review=review,
            rating=rating,
            customer=current_user,
            product=prod
        )
        db.session.add(new_review)
        db.session.commit()


    except:
        error = True
        db.session.rollback()

    finally:
        db.session.close()
    if error:
        app.logger.info('Info level log')
        app.logger.warning('Warning level log')
        app.logger.error('Error level log')
        app.logger.critical('Critical level log')
        abort(400)
    else:
        return jsonify({"success": True})
