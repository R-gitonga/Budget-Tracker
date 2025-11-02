from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from sqlalchemy import text
from datetime import datetime

from app.models import Category, Goal, Transaction, User
from app import db
from app.forms import GoalForm, TransactionForm, CategoryForm, RegistrationForm, LoginForm


bp = Blueprint('main', __name__)


@bp.route('/')
def home():
    return render_template('home.html')




# Transactions Route
@bp.route('/transactions')
@login_required
def transactions():
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
    .order_by(Transaction.date.desc()).all()

    income = sum(t.amount for t in transactions if t.amount > 0)
    expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
    balance = income - expenses
    return render_template('transactions.html', transactions=transactions, income=income, expenses=expenses, balance=balance)

# Add Transaction Route
@bp.route('/transactions/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    form = TransactionForm()
    form.category_id.choices = [
    (c.id, c.name) for c in Category.query.filter_by(user_id=current_user.id).all()] # Load Categories

    if form.validate_on_submit():
        new_tx = Transaction(
            description=form.description.data,
            amount=form.amount.data,
            date=form.date.data,
            category_id=form.category_id.data,
            user_id=current_user.id  # ✅ Assign user here

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
    # Only allow the user to edit their own transactions
    tx = Transaction.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    form = TransactionForm(obj=tx)
    form.category_id.choices = [
        (c.id, c.name) for c in Category.query.filter_by(user_id=current_user.id).all()
    ]

    if form.validate_on_submit():
        tx.description = form.description.data
        tx.amount = form.amount.data
        tx.date = form.date.data
        tx.category_id = form.category_id.data

        db.session.commit()
        flash('Transaction updated successfully!', 'success')
        return redirect(url_for('main.transactions'))

    if form.errors:
        flash('Please correct the errors below.', 'danger')

    return render_template('edit_transaction.html', form=form, tx=tx)

#  Delete transaction
@bp.route('/transactions/delete/<int:id>', methods=['GET'])
@login_required
def delete_transaction(id):
    transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first_or_404(id)
    db.session.delete(transaction)
    db.session.commit()
    flash('Transaction deleted successfully!', 'success')
    return redirect(url_for('main.transactions'))



# Add Categories Route
@bp.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    form = CategoryForm()
    categories = Category.query.filter_by(user_id=current_user.id).all()

    if form.validate_on_submit():
        new_category = Category(
            name=form.name.data.strip(),
            user_id=current_user.id
            
            )
        db.session.add(new_category)
        db.session.commit()
        flash('Category added successfully!', "success")
        return redirect(url_for('main.categories'))
    
    return render_template('categories.html', form=form, categories=categories)

@bp.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = Category.query.filter_by(id=id, user_id=current_user.id).first_or_404(id)
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
    category = Category.query.filter_by(id=id, user_id=current_user.id).first_or_404()

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

    if not name:
        flash('Category name cannot be empty!', 'danger')
        return redirect(url_for('main.add_transaction'))

    # ✅ Ensure category names are unique *per user*, not globally
    existing = Category.query.filter_by(name=name, user_id=current_user.id).first()
    if existing:
        flash('You already have a category with that name!', 'warning')
    else:
        new_category = Category(
            name=name,
            user_id=current_user.id
        )
        db.session.add(new_category)
        db.session.commit()
        flash('Category added successfully!', 'success')

    return redirect(url_for('main.add_transaction'))





# Analytics
@bp.route('/analytics')
@login_required
def analytics():
    # Get all transactions for the logged-in user
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()

    # Compute income, expenses, and balance
    income = sum(t.amount for t in transactions if t.amount > 0)
    expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
    balance = income - expenses

    # Spending by category (filtered by user)
    user_categories = Category.query.filter_by(user_id=current_user.id).all()
    categories = [c.name for c in user_categories]
    category_amounts = [
        sum(abs(t.amount) for t in transactions if t.category_id == c.id and t.amount < 0)
        for c in user_categories
    ]

    # Spending over time (grouped by date)
    from collections import defaultdict
    from datetime import datetime

    daily_spending = defaultdict(float)
    for t in transactions:
        date_str = t.date.strftime("%Y-%m-%d") if isinstance(t.date, datetime) else str(t.date)
        daily_spending[date_str] += t.amount

    dates = list(daily_spending.keys())
    daily_totals = list(daily_spending.values())

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


# Goals
# View all goals
@bp.route('/goals')
@login_required
def goals():
    user_goals = Goal.query.filter_by(user_id=current_user.id).all()
    return render_template('goals.html', goals=user_goals)

# Add new goal
@bp.route('/goals/add', methods=['GET', 'POST'])
@login_required
def add_goal():
    form = GoalForm()
    form.category_id.choices = [
    (c.id, c.name) for c in Category.query.filter_by(user_id=current_user.id).all()]

    if form.validate_on_submit():
        
        new_goal = Goal(
            name=form.name.data,
            description=form.description.data,
            target_amount=form.target_amount.data or 0,
            current_amount=form.current_amount.data or 0,
            deadline=form.deadline.data,
            progress=form.progress.data or 0,
            status=form.status.data,
            user_id=current_user.id,
            category_id=form.category_id.data
        )
        new_goal.progress = (new_goal.current_amount / new_goal.target_amount * 100) if new_goal.target_amount > 0 else 0.0
        db.session.add(new_goal)
        db.session.commit()
        print('✅ Form Submitted')
        flash('New goal added successfully!', 'success')
        return redirect(url_for('main.goals'))
    return render_template('add_goal.html', form=form)

# View goal details
@bp.route('/goals/<int:id>')
@login_required
def view_goal(id):
    goal = Goal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template('goals/view_goal.html', goal=goal)


# Edit goal
@bp.route('/goals/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_goal(id):
    goal = Goal.query.filter_by(id=id, user_is=current_user.id).first_or_404()

    if request.method == 'POST':
        goal.name = request.form['name']
        goal.target_amount = float(request.form['target_amount']) or 0
        goal.current_amount = float(request.form['current_amount']) or 0
        goal.deadline = request.form['deadline']
        goal.status = request.form['status']
        goal.progress = (goal.current_amount / goal.target_amount) * 100 if goal.target_amount else 0
        db.session.commit()
        flash('Goal updated successfully!', 'success')
        return redirect(url_for('main.goal'))
    return render_template('goals/edit_goal.html', goal=goal)

# delete goal
@bp.route('/goals/delete/<int:id>', methods=['POST'])
def delete_goal(id):
    goal = Goal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    flash('Goal deleted successfully', 'success')
    return redirect(url_for('main.goals'))