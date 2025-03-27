from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField,DateTimeLocalField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField
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


#subject form
class SubjectForm(FlaskForm):
    name= StringField('Subject Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit= SubmitField('Add Subject')

#chapter form
class ChapterForm(FlaskForm):
    name= StringField('Chapter Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    subject_id= SelectField('Subject', coerce=int, validators=[DataRequired()])
    submit= SubmitField('Add Chapter')

#quiz form
class QuizForm(FlaskForm):
    name= StringField('Quiz Name', validators=[DataRequired()])
    date_of_quiz= DateTimeLocalField('Date of Quiz', validators=[DataRequired()])
    time_duration= IntegerField('Time Duration (in minutes)', validators=[DataRequired()])
    chapter_id= SelectField('Chapter', coerce=int, validators=[DataRequired()])
    submit= SubmitField('Add Quiz')

#Question
class QuestionForm(FlaskForm):
     question_statement = TextAreaField('Question Statement', validators=[DataRequired()])
     option1 = StringField('Option 1', validators=[DataRequired()])
     option2 = StringField('Option 2', validators=[DataRequired()])
     option3 = StringField('Option 3', validators=[DataRequired()])
     option4 = StringField('Option 4', validators=[DataRequired()])
     correct_option = IntegerField('Correct Option (1-4)', validators=[DataRequired()])
     submit = SubmitField('Add Question')