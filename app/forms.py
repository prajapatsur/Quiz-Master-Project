from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo

#user registration form
class RegisterForm(FlaskForm):
    username = StringField('Email', validators=[DataRequired(), Email()])   #as we are using Email() so wee need to import it from wtforms.validators
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    fullname = StringField('Full Name')
    qualification = StringField('Qualification')
    dob = DateField('Date of Birth', format='%Y-%m-%d')
    is_admin = BooleanField('Admin', default=False)
    submit = SubmitField('Register')

#user login form
class LoginForm(FlaskForm):
    username = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5)])
    submit = SubmitField('Login')
