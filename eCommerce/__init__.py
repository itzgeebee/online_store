from functools import wraps
import os
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import  LoginManager
# from forms import CreatePostForm, CreateUserForm, LoginUserForm, CommentForm
from flask_gravatar import Gravatar
from flask_mail import Mail


file_path = os.path.abspath(os.getcwd())+"/test.db"

login_manager = LoginManager()
app = Flask(__name__)
login_manager.init_app(app)
app.config['SECRET_KEY'] = os.urandom(10)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{file_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv("EMAIL")
app.config['MAIL_PASSWORD'] = os.environ.get("EMAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = "noreply@laptohaven.com"
app.config['STRIPE_PUBLIC_KEY'] = os.environ["STRIPE_PUBLIC"]
app.config['STRIPE_SECRET_KEY'] = os.environ.get("STRIPE_PRIVATE")
db = SQLAlchemy(app)
mail_sender = Mail(app)

from eCommerce import views

