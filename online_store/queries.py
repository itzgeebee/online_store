from flask import (render_template,
                   redirect, url_for,
                   flash, request,
                   jsonify, session)
from online_store.models import (Customer, Product,
                                 Reviews)
from online_store import app, db, login_manager
from flask_login import (login_required,
                         current_user)


@login_manager.user_loader
def load_user(id):
    return Customer.query.get(id)


@app.route("/", methods=["GET", "POST"])
def home():

    message = request.args.get("message")
    page = request.args.get("page", 1, type=int)
    all_prods = Product.query.with_entities(Product.id,
                                            Product.img_url,
                                            Product.price,
                                            Product.product_description,
                                            ).paginate(per_page=64,
                                                       page=page)

    prod_list = []
    for i in all_prods.items:
        prod = {
            "id": i.id,
            "img_url": i.img_url,
            "product_description": i.product_description,
            "price": i.price
        }
        prod_list.append(prod)

    page_url = 'home'
    app.logger.info('Info level log')
    app.logger.warning('Warning level log')
    app.logger.error('Error level log')
    app.logger.critical('Critical level log')
    return render_template("index.html", prods=prod_list,
                           pages=all_prods,
                           logged_in=current_user.is_authenticated,
                           page_url=page_url, message=message
                           )


@app.route("/product")
def product():
    product_id = request.args.get("id")
    specific_product = Product.query.get(product_id)
    all_reviews = Reviews.query.filter_by(product_id=product_id)
    if specific_product:
        prod_orders = [i.order_name for i in specific_product.order]



        app.logger.info('Info level log')
        app.logger.warning('Warning level log')
        app.logger.error('Error level log')
        app.logger.critical('Critical level log')
        return render_template("product.html", prod=specific_product,
                               logged_in=current_user.is_authenticated,
                               rev=all_reviews, prod_orders=prod_orders)


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        product_id = request.form.get("product")
        session['search'] = product_id
    else:
        if "search" in session:
            product_id = session.get("search")

    page = request.args.get("page", 1, type=int)
    query_result = Product.query.with_entities(Product.id,
                                               Product.img_url,
                                               Product.price,
                                               Product.product_description
                                               ).filter(
        Product.product_name.ilike(f"%{product_id}%") | Product.product_description.ilike(f"%{product_id}%")
        | Product.category.ilike(f"%{product_id}%")).paginate(per_page=40, page=page)

    if query_result:
        result_list = []
        for i in query_result.items:
            rez = {
                "id": i.id,
                "img_url": i.img_url,
                "product_description": i.product_description,
                "price": i.price
            }
            result_list.append(rez)
        page_url = "search"
    else:
        error = "Nothing found"
        app.logger.info('Info level log')
        app.logger.warning('Warning level log')
        app.logger.error('Error level log')
        app.logger.critical('Critical level log')
        return redirect(url_for("home", message=error))
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
    filter_result = Product.query.with_entities(Product.id,
                                                Product.img_url,
                                                Product.price,
                                                Product.product_description
                                                ).filter(
        Product.price > min_price,
        Product.price < max_price,
        Product.category == category).paginate(per_page=56, page=page)
    if filter_result:
        result_list = []
        for i in filter_result.items:
            rez = {
                "id": i.id,
                "img_url": i.img_url,
                "product_description": i.product_description,
                "price": i.price
            }
            result_list.append(rez)
        page_url = 'filter'
        return render_template("index.html", prods=result_list, pages=filter_result,
                               logged_in=current_user.is_authenticated, page_url=page_url
                               )
    else:
        error = "Nothing found"

        app.logger.error('Error level log')
        app.logger.critical('Critical level log')
        return redirect(url_for("home", message=error))


