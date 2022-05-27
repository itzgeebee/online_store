import os


file_path = os.path.abspath(os.getcwd()) + "/test.db"

SECRET_KEY = os.urandom(10)
SQLALCHEMY_DATABASE_URI = f"sqlite:///{file_path}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = os.getenv("EMAIL")
MAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
MAIL_DEFAULT_SENDER = "noreply@laptohaven.com"
STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_PRIVATE")
DEBUG=True