import os
from datetime import timedelta

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
# from forms import CreatePostForm, CreateUserForm, LoginUserForm, CommentForm
from flask_gravatar import Gravatar
from flask_mail import Mail
from flask_migrate import Migrate




file_path = os.path.abspath(os.getcwd()) + "/test.db"

login_manager = LoginManager()
app = Flask(__name__)
login_manager.init_app(app)
app.config['SECRET_KEY'] = os.urandom(10)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{file_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv("EMAIL")
app.config['MAIL_PASSWORD'] = os.environ.get("EMAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = "noreply@laptohaven.com"
app.config['STRIPE_PUBLIC_KEY'] = os.environ.get("STRIPE_PUBLIC")
app.config['STRIPE_SECRET_KEY'] = os.environ.get("STRIPE_PRIVATE")
app.permanent_session_lifetime = timedelta(days=30)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail_sender = Mail(app)
Bootstrap(app)
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

from online_store import views
from online_store import admin_views
