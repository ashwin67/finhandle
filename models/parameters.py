from app import db

class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("fin_user.id"))

    user = db.relationship("FinUser", back_populates="accounts")
    transactions = db.relationship("Transaction", back_populates="account")

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("fin_user.id"))

    user = db.relationship("FinUser", back_populates="categories")
    transactions = db.relationship("Transaction", back_populates="category")

class KeywordCategoryMapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('fin_user.id'))
    keyword = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    comparison = db.Column(db.String(1), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<KeywordCategoryMapping {self.id}: {self.keyword} -> {self.category_id}>"