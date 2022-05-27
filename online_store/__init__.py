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

login_manager = LoginManager()
app = Flask(__name__)
app.config.from_object('config')
login_manager.init_app(app)
app.permanent_session_lifetime = timedelta(days=30)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail_sender = Mail(app)
Bootstrap(app)
gravatar = Gravatar(app,
                    size=50,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

from online_store import views
from online_store import admin_views
