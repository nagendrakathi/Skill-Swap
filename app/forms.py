from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    # Custom validators
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose another one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use another one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class SkillForm(FlaskForm):
    name = StringField('Skill Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = SelectField('Category', validators=[DataRequired()], 
                         choices=[
                             ('programming', 'Programming'),
                             ('languages', 'Languages'),
                             ('music', 'Music'),
                             ('cooking', 'Cooking'),
                             ('arts', 'Arts & Crafts'),
                             ('fitness', 'Health & Fitness'),
                             ('academic', 'Academic Subjects'),
                             ('business', 'Business Skills'),
                             ('other', 'Other')
                         ])
    difficulty = SelectField('Difficulty Level', validators=[DataRequired()],
                           choices=[
                               ('beginner', 'Beginner'),
                               ('intermediate', 'Intermediate'),
                               ('advanced', 'Advanced')
                           ])
    submit = SubmitField('Add Skill')

class RequestForm(FlaskForm):
    message = TextAreaField('Message (Optional)', validators=[Length(max=500)])
    submit = SubmitField('Send Request')

class ProfileForm(FlaskForm):
    bio = TextAreaField('About Me', validators=[Length(max=500)])
    location = StringField('Location', validators=[Length(max=100)])
    submit = SubmitField('Update Profile')

class MessageForm(FlaskForm):
    content = TextAreaField('Message', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Send')

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', validators=[DataRequired()],
                      choices=[(str(i), str(i)) for i in range(1, 6)])
    comment = TextAreaField('Comment', validators=[Length(max=500)])
    submit = SubmitField('Submit Review')