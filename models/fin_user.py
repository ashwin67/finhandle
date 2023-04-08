from flask_login import UserMixin
from app import db
from models.transaction import Transaction
from sqlalchemy import extract
from datetime import datetime
from models.parameters import KeywordCategoryMapping

class FinUser(UserMixin, db.Model):
    __tablename__ = 'fin_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    accounts = db.relationship("Account", back_populates="user")
    categories = db.relationship("Category", back_populates="user")
    custom_mappings = db.Column(db.JSON, nullable=True)

    def __repr__(self):
        return f"<FinUser {self.username}>"

    # Flask-Login required methods and properties
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def get_transactions(self):
        return Transaction.query.filter_by(user_id=self.id)

    @property
    def total_balance(self):
        transactions = self.get_transactions()
        return sum(transaction.amount for transaction in transactions)

    def get_monthly_spending_by_category(self, year):
        transactions = self.get_transactions().filter(
            extract('year', Transaction.date) == year
        )
        categories = set(transaction.category for transaction in transactions)
        categories.add(None)  # Add None to the set of categories to account for transactions without a category
        monthly_spending_by_category = {str(category): [0] * 12 for category in categories}

        for transaction in transactions:
            month = transaction.date.month - 1  # Subtract 1 because list indices start at 0
            category = transaction.category
            amount = transaction.amount
            if category is not None:
                category_key = str(category)
                monthly_spending_by_category[category_key][month] += amount
            else:
                # You can decide what to do when the category is None
                # For example, you can create an "Uncategorized" category
                uncategorized = "Uncategorized"
                if uncategorized not in monthly_spending_by_category:
                    monthly_spending_by_category[uncategorized] = [0] * 12
                monthly_spending_by_category[uncategorized][month] += amount

        return monthly_spending_by_category
    
    def apply_keyword_mappings(self, transaction):
        mappings = KeywordCategoryMapping.query.filter_by(user_id=self.id).all()

        for mapping in mappings:
            if mapping.keyword.lower() in transaction.description.lower():
                if (
                    (mapping.comparison == "<" and transaction.amount < mapping.amount) or
                    (mapping.comparison == "=" and transaction.amount == mapping.amount) or
                    (mapping.comparison == ">" and transaction.amount > mapping.amount)
                ):
                    transaction.category_id = mapping.category_id
                    db.session.commit()
                    break
