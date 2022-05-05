from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, TextAreaField, BooleanField, DateField, \
    SelectField, IntegerField
from wtforms.validators import DataRequired, URL, Length


class CreateUserForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=30)], id="password_field")
    # show_password = BooleanField('Show password', id='check')
    confirm_password = PasswordField("confirm password", validators=[DataRequired(), Length(min=6, max=25)])
    name = StringField("Name", validators=[DataRequired(), Length(min=2)])
    street = StringField("Name", validators=[DataRequired(), Length(min=2)])

    submit = SubmitField("Register")


class LoginUserForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign in")
