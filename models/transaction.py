from datetime import datetime
from app import db

class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"))
    account = db.relationship('Account', back_populates="transactions")
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    category = db.relationship('Category', back_populates="transactions")
    user_id = db.Column(db.Integer, db.ForeignKey("fin_user.id"), nullable=False)
    user = db.relationship('FinUser', backref=db.backref('transactions', lazy=True))
