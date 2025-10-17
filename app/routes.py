from flask import Blueprint, render_template, redirect, url_for, request, flash
from sqlalchemy import text
from datetime import datetime

from app.models import Category, Transaction
from app import db
from app.forms import TransactionForm, CategoryForm

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    try:
        # simple query to check DB connection
        db.session.execute(text('SELECT 1'))
        flash('Database connected successfully!', "success")
    except Exception as e:
        flash(f"Database connection failed: {str(e)}", "danger")
    return render_template('dashboard.html')


# Transactions Route
@bp.route('/transactions')
def transactions():
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    return render_template('transactions.html', transactions=transactions)

# Add Transaction Route
@bp.route('/transactions/add', methods=['GET', 'POST'])
def add_transaction():
    form = TransactionForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()] # Load Categories

    if form.validate_on_submit():
        new_tx = Transaction(
            description=form.description.data,
            amount=form.amount.data,
            date=form.date.data,
            category_id=form.category_id.data
        )
        db.session.add(new_tx)
        db.session.commit()
        flash('Transaction added successfully!', "success")
        return redirect(url_for('main.transactions'))
    if form.errors:
        flash('Please fix the errors below.', "danger")

    return render_template('add_transaction.html', form=form)

# Add Categories Route
@bp.route('/categories', methods=['GET', 'POST'])
def categories():
    form = CategoryForm()
    categories = Category.query.all()

    if form.validate_on_submit():
        new_category = Category(name=form.name.data.strip())
        db.session.add(new_category)
        db.session.commit()
        flash('Category added successfully!', "success")
        return redirect(url_for('main.categories'))
    
    return render_template('categories.html', form=form, categories=categories)
