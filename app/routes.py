from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from sqlalchemy import text
from datetime import datetime

from app.models import Category, Transaction, User
from app import db
from app.forms import TransactionForm, CategoryForm, RegistrationForm, LoginForm


bp = Blueprint('main', __name__)


@bp.route('/')
@login_required
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
@login_required
def transactions():
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()

    income = sum(t.amount for t in transactions if t.amount > 0)
    expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
    balance = income - expenses
    return render_template('transactions.html', transactions=transactions, income=income, expenses=expenses, balance=balance)

# Add Transaction Route
@bp.route('/transactions/add', methods=['GET', 'POST'])
@login_required
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



# Edit transaction
@bp.route('/transactions/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(id):
    tx = Transaction.query.get_or_404(id)
    form = TransactionForm(obj=tx)  # prefill the form with the existing transaction data
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]  # load category list

    if form.validate_on_submit():
        tx.description = form.description.data
        tx.amount = form.amount.data
        tx.date = form.date.data
        tx.category_id = form.category_id.data

        db.session.commit()
        flash('Transaction updated successfully!', 'success')
        return redirect(url_for('main.transactions'))
    elif form.errors:
        flash('Please correct the errors below.', 'danger')

    return render_template('edit_transaction.html', form=form, transaction=tx)

# @bp.route('/transactions/view/<int:id>', methods=['GET'])
# @login_required

#  Delete transaction
@bp.route('/transactions/delete/<int:id>', methods=['GET'])
@login_required
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    db.session.delete(transaction)
    db.session.commit()
    flash('Transaction deleted successfully!', 'success')
    return redirect(url_for('main.transactions'))



# Add Categories Route
@bp.route('/categories', methods=['GET', 'POST'])
@login_required
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

@bp.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    form = CategoryForm(obj=category)

    if form.validate_on_submit():
        category.name = form.name.data.strip()
        db.session.commit()
        flash('Category updated successfully!', 'success')
        return redirect(url_for('main.categories'))

    return render_template('edit_category.html', form=form, category=category)

@bp.route('/categories/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    category = Category.query.get_or_404(id)

     # Check if category has transactions
    if category.transactions:
        flash("Cannot delete this category because it has linked transactions.", "danger")
        return redirect(url_for('main.categories'))

    db.session.delete(category)
    db.session.commit()

    flash('Category deleted successfully!', 'success')
    return redirect(url_for('main.categories'))

# Add category from transactions form
@bp.route('/categories/add-modal', methods=['POST'])
@login_required
def add_category_modal():
    name = request.form.get('name', '').strip()
    if name:
        existing = Category.query.filter_by(name=name).first()
        if existing:
            flash('Category already exists!', 'warning')
        else:
            new_category = Category(name=name)
            db.session.add(new_category)
            db.session.commit()
            flash('Category added successfully!', 'success')
    else:
        flash('Category name cannot be empty!', 'danger')
    return redirect(url_for('main.add_transaction'))





# Analytics
@bp.route('/analytics')
@login_required
def analytics():
    transactions = Transaction.query.all()

    # Income and expense totals
    income = sum(t.amount for t in transactions if t.amount > 0)
    expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
    balance = income - expenses

    # Spending by category
    categories = [c.name for c in Category.query.all()]
    category_amounts = []
    for c in Category.query.all():
        total = sum(abs(t.amount) for t in transactions if t.category_id == c.id and t.amount < 0)
        category_amounts.append(total)

    # spending over time (grouped by date)

    from collections import defaultdict
    from datetime import datetime

    daily_spending = defaultdict(float)
    for t in transactions:
        date_str = t.date.strftime("%Y-%m-%d") if isinstance(t.date, datetime) else str(t.date)
        daily_spending[date_str] += t.amount

    dates = list(daily_spending.keys())
    daily_totals = list(daily_spending.values())

    print("DATES:", dates)
    print("TOTALS:", daily_totals)



    return render_template(
        'analytics.html',
        income=income,
        expenses=expenses,
        balance=balance,
        categories=categories,
        category_amounts=category_amounts,
        dates=dates,
        daily_totals=daily_totals
    )

