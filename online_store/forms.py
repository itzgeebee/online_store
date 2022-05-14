from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, TextAreaField, BooleanField, DateField, \
    SelectField, IntegerField, URLField
from wtforms.validators import DataRequired, URL, Length


class CreateUserForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=30)], id="password_field")
    # show_password = BooleanField('Show password', id='check')
    confirm_password = PasswordField("confirm password", validators=[DataRequired(), Length(min=6, max=25)])
    first_name = StringField("First Name", validators=[DataRequired(), Length(min=2)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(min=2)])
    street = StringField("Street", validators=[DataRequired(), Length(min=2)])
    city = StringField("City", validators=[DataRequired(), Length(min=2)])
    zip = StringField("Zip", validators=[DataRequired(), Length(min=2, max=8)])
    phone = StringField("Phone", validators=[DataRequired(), Length(min=2, max=12)])
    submit = SubmitField("Register")


class LoginUserForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign in")


class ChangePassword(FlaskForm):
    old_password = PasswordField("Old Password", validators=[DataRequired()])
    new_password = PasswordField("New  Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class ResetPassword(FlaskForm):
    new_password = PasswordField("New  Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class EditUserForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    first_name = StringField("First Name", validators=[DataRequired(), Length(min=2)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(min=2)])
    street = StringField("Street", validators=[DataRequired(), Length(min=2)])
    city = StringField("City", validators=[DataRequired(), Length(min=2)])
    zip = StringField("Zip", validators=[DataRequired(), Length(min=2, max=8)])
    phone = StringField("Phone", validators=[DataRequired(), Length(min=2, max=12)])
    submit = SubmitField("Submit")


class UploadForm(FlaskForm):
    quantity = IntegerField("Quantity", validators=[DataRequired()], default=100)
    product_name = StringField("Product name", validators=[DataRequired()])
    product_description = StringField("Description", validators=[DataRequired()])
    category = SelectField("Category", choices=["Phone", "Laptop"], validators=[DataRequired()])
    price = IntegerField("Price", validators=[DataRequired()])
    img_url = URLField("Image url", validators=[DataRequired()])
    submit = SubmitField("Submit")
