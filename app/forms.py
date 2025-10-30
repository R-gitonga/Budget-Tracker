from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, FloatField, SelectField, DateField, SubmitField, PasswordField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, NumberRange, Length, Email, Optional, EqualTo

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Add Category')

class TransactionForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired()])
    amount = FloatField('Amount (Ksh)', validators=[DataRequired(), NumberRange(min=-1000000, max=1000000)])
    date = DateField('Date', validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Transaction')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Login')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class GoalForm(FlaskForm):
    name = StringField('Goal Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    target_amount = FloatField('Target Amount', validators=[DataRequired()])
    deadline = DateField('Deadline', format='%Y-%m-%d', validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    progress = FloatField('Progress', default=0, validators=[Optional()])
    status = StringField('Status', default='Not Started', validators=[Optional()])
    submit = SubmitField('Save Goal')
