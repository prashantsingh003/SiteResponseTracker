import re
from time import sleep
from flask_wtf import FlaskForm
import requests
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, BooleanField, RadioField
from wtforms.validators import DataRequired,Length,EqualTo, Email,ValidationError,InputRequired
# from flaskblog.models import User

class RegistrationForm(FlaskForm):
    username=StringField('Full Name',
                        validators=[InputRequired(message="Please enter a user name"), Length(min=2,max=20)])
    email=StringField('Email',
                        validators=[DataRequired()])
    password= PasswordField('Password',validators=[DataRequired()])
    confirm_password= PasswordField('Confirm Password',
                        validators=[DataRequired(), EqualTo('password')])
    submit=SubmitField('Sign Up')

    # def validate_username(self,username):
    #     user=User.query.filter_by(username=username.data).first()
    #     if user:
    #         raise ValidationError('The username is taken. Please take a diffrent name')
    
    def validate_email(self,email):
        regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        if not re.fullmatch(regex,email.data):
            raise ValidationError('Please enter a valid email')

class LoginForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired()])
    password= PasswordField('Password',validators=[DataRequired()])
    remember=BooleanField('Remember Me')
    submit=SubmitField('Login')

    # def validate_email(self,email):
    #     regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    #     if not re.fullmatch(regex,email.data):
    #         raise ValidationError('Please enter a valid email')
class ResetPasswordForm(FlaskForm):
    password= PasswordField('Password',validators=[DataRequired()])
    confirm_password= PasswordField('Confirm Password',
                        validators=[DataRequired(), EqualTo('password')])
    submit=SubmitField('Submit')

    

class AddWebsiteForm(FlaskForm):
    role = RadioField('Role', choices = [('VIEWER','Viewer'),('OWNER','Owner')]) 
    url=StringField('Site Address',validators=[DataRequired()])
    notify = RadioField('Notifications', choices = [(True,'Yes'),(False,'No')])
    submit=SubmitField('Submit')

    # def validate_url(self,url):
    #     try:
    #         res=requests.get(url.data,timeout=5)

    #     except Exception as ex:
    #         raise ValidationError(ex)
        