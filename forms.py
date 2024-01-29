from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, InputRequired, NumberRange, ValidationError


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign Up")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")
  
       

class SearchForm(FlaskForm):
    isbn = StringField('ISBN')
    title = StringField('Title')
    author = StringField('Author')
    submit = SubmitField("Search")



       


class ReviewForm(FlaskForm):
    rating = IntegerField("Rating (1-5)", validators=[InputRequired(), NumberRange(min=1, max=5)])
    content = TextAreaField("Your Review", validators=[InputRequired()])
    submit = SubmitField("Submit Review")
   