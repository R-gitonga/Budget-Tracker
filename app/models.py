from app import db
from datetime import datetime

# category table
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    # relationship to transaction
    transactions = db.relationship('Transaction', backref='category_ref', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date=db.Column(db.Date, default=datetime.utcnow)
    description = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    # foregin key to category
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    def __repr__(self):
        return f"<Transaction {self.description} - {self.amount}>"