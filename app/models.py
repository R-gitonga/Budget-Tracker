from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Goals table
class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    target_amount = db.Column(db.Float, nullable=False)
    deadline = db.Column(db.Date, nullable=False)
    progress = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default="Not Started")

    # Each goal belong to a user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # optional: Link to category for financial grouping
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Goal {self.name} - {self.status}>"
        
# users table
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    transactions = db.relationship('Transaction', backref='user', lazy=True)
    categories = db.relationship('Category', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# category table
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_category_user_id'), nullable=False)
    # relationship to transaction
    transactions = db.relationship('Transaction', backref='category_ref', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date=db.Column(db.Date, default=datetime.utcnow)
    description = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_trnsaction_user_id'), nullable=False)
    # foregin key to category
    category_id = db.Column(db.Integer, db.ForeignKey('category.id', name='fk_transaction_category_id'), nullable=False)

    def __repr__(self):
        return f"<Transaction {self.description} - {self.amount}>"