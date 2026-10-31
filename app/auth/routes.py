from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import User
from app.forms import RegistrationForm, LoginForm

bp = Blueprint('auth', __name__)


# Registration Route
@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data.lower())
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            # Two people registering the same name at the same moment can slip past the form check.
            db.session.rollback()
            flash('That username or email is already registered.', 'danger')
            return render_template('auth/register.html', form=form)
        flash('Account created successfully! please login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(func.lower(User.email) == form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Welcome back', 'success')
            return redirect(url_for('main.transactions'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('auth/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))