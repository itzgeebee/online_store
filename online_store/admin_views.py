import os
from flask import (render_template, redirect,
                   url_for, request,
                   send_file, session, jsonify)
from sqlalchemy import asc

from online_store.models import (Customer, Product, Order,
                                 Reviews, OrderDetails)
from werkzeug.exceptions import abort
from online_store import app, login_manager
from flask_login import current_user
from online_store import db
from functools import wraps
from online_store.forms import UploadForm
import csv


@login_manager.user_loader
def load_user(id):
    return Customer.query.get(id)


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1 or not current_user.is_authenticated:
            return abort(403, description="Forbidden! You do not have access to this page")
        return f(*args, **kwargs)

    return decorated_function


@app.route("/admin", methods=["GET", "POST"])
@admin_only
def admin_home():
    return render_template("admin.html",
                           logged_in=current_user.is_authenticated)


@app.route("/admin/inventory", methods=["GET", "POST"])
@admin_only
def inventory():
    try:
        os.remove(os.path.abspath(os.getcwd()) + "/Inventory.csv")
    except FileNotFoundError:
        pass
    page = request.args.get("page", 1, type=int)
    all_prods = Product.query.order_by(Product.quantity.asc()).paginate(per_page=100, page=page)

    prod_list = [product.to_dict() for product in all_prods.items]

    page_url = 'inventory'
    return render_template("inventory.html", prods=prod_list, pages=all_prods,
                           logged_in=current_user.is_authenticated, page_url=page_url)


@app.route("/admin/restock", methods=["GET", "POST"])
@admin_only
def restock():
    product_to_restock = request.args.get("prod_id")
    product = Product.query.get(product_to_restock)
    product.quantity = 100
    db.session.commit()

    return redirect(url_for('inventory'))


@app.route("/admin/sales", methods=["GET", "POST"])
@admin_only
def sales():
    try:
        os.remove(os.path.abspath(os.getcwd()) + "/Sales.csv")
    except FileNotFoundError:
        pass
    page = request.args.get("page", 1, type=int)
    all_sales = Order.query.order_by(Order.quantity.desc()).paginate(per_page=100, page=page)


    sales_list = []


    for i in all_sales.items:
        order_dets = OrderDetails.query.get(i.order_details_id)
        prod = {
            "customer_id": order_dets.customer_id,
            "product_id": i.product_id,
            "quantity": i.quantity,
            "order_date": order_dets.order_date
        }
        sales_list.append(prod)
    page_url = 'inventory'
    return render_template("sales.html", prods=sales_list, pages=all_sales,
                           logged_in=current_user.is_authenticated, page_url=page_url)


@app.route("/admin/upload", methods=["GET", "POST"])
@admin_only
def upload():
    upload_form = UploadForm()
    if upload_form.validate_on_submit():
        new_product = Product(
            quantity=upload_form.quantity.data,
            product_name=upload_form.product_name.data,
            product_description=upload_form.product_description.data,
            category=upload_form.category.data,
            price=upload_form.price.data,
            img_url=upload_form.img_url.data
        )
        db.session.add(new_product)
        db.session.commit()
        message = "New product added"
        return redirect(url_for('inventory', message=message))

    return render_template("edit.html", form=upload_form,
                           logged_in=current_user.is_authenticated)


@app.route("/admin/edit", methods=['GET', "POST"])
@admin_only
def edit():
    product_id = request.args.get("prod_id")
    product_to_edit = Product.query.get(product_id)
    edit_form = UploadForm(
        quantity=product_to_edit.quantity,
        product_name=product_to_edit.product_name,
        product_description=product_to_edit.product_description,
        category=product_to_edit.category,
        price=product_to_edit.price,
        img_url=product_to_edit.img_url
    )
    if edit_form.validate_on_submit():
        product_to_edit.quantity = edit_form.quantity.data
        product_to_edit.product_name = edit_form.product_name.data
        product_to_edit.product_description = edit_form.product_description.data
        product_to_edit.category = edit_form.category.data
        product_to_edit.price = edit_form.price.data
        product_to_edit.img_url = edit_form.img_url.data

        db.session.commit()
        message = "edited successfully"
        return redirect(url_for('inventory', message=message))
    return render_template('edit.html', form=edit_form)


@app.route("/admin/delete")
@admin_only
def delete():
    product_id = request.args.get("prod_id")
    product_to_delete = Product.query.get(product_id)
    db.session.delete(product_to_delete)
    db.session.commit()
    message = "Deleted successfully"
    return redirect(url_for('inventory', message=message))


@app.route("/admin/generate-inventory-report")
@admin_only
def generate_report():
    all_prods = Product.query.all()

    prod_list = []
    for i in all_prods:
        prod = i.to_dict()
        prod_list.append(prod)
    csv_columns = ["id", "quantity", "product_name", "product_description", "category", "price", "img_url"]
    csv_file = os.path.abspath(os.getcwd()) + "/Inventory.csv"

    try:
        with open(csv_file, 'w', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in prod_list:
                print(data)
                writer.writerow(data)
    except IOError as e:
        print(e)

    return send_file(csv_file, as_attachment=True)


@app.route("/admin/generate-sales-report")
@admin_only
def generate_sales():

    all_prods = Order.query.all()

    prod_list = []
    for i in all_prods:
        order_dets = OrderDetails.query.get(i.order_details_id)

        prod = {
            "customer_id": order_dets.customer_id,
            "product_id": i.product_id,
            "quantity": i.quantity,
            "order_date": order_dets.order_date,
            "to_street": order_dets.to_street,
            "to_city": order_dets.to_city,
            "zip": order_dets.zip
        }
        prod_list.append(prod)
    csv_columns = ["id", "customer_id", "product_id", "quantity", "to_street", "to_city", "zip", "order_date"]
    csv_file = os.path.abspath(os.getcwd()) + "\Sales.csv"

    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in prod_list:
                writer.writerow(data)
    except IOError as e:
        print(e)

    return send_file(csv_file, as_attachment=True)


@app.route("/admin/reviews")
@admin_only
def reviews():
    page = request.args.get("page", 1, type=int)
    revs = Reviews.query.order_by(asc(Reviews.rating)).paginate(per_page=150, page=page)
    page_url = "reviews"
    rev_list = [rev.to_dict() for rev in revs.items]

    return render_template("reviews.html", reviews=rev_list,
                           logged_in=current_user.is_authenticated,
                           pages=revs, page_url=page_url)

@app.route("/delete-review")
def delete_review():
    rev_id = request.args.get("id")
    rev_to_delete = Reviews.query.get(rev_id)
    db.session.delete(rev_to_delete)
    db.session.commit()
    return redirect(url_for("reviews"))