from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import current_user, LoginManager
from flask_login import login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, extract
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from datetime import datetime
from flask import jsonify
from flask_login import login_required


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finhandle.db'  # Use the appropriate database URI for your setup
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)  # Generate a random key for secure sessions

db = SQLAlchemy()
db.init_app(app)

from models.fin_user import FinUser
from models.transaction import Transaction
from models.parameters import Account, Category

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Google OAuth2 client ID and secret
GOOGLE_CLIENT_ID = "your_google_client_id_here"
GOOGLE_CLIENT_SECRET = "your_google_client_secret_here"
GOOGLE_DISCOVERY_DOC = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

from views.forms import TransactionUploadForm, AddAccountForm, AddCategoryForm
from views.auth import auth
from views.import_transactions import parse_transactions
app.register_blueprint(auth, url_prefix='/auth')


@app.route('/')
def index():
    if current_user.is_authenticated:
        total_balance = current_user.total_balance
        categories = Category.query.filter_by(user_id=current_user.id).all()
        transactions = Transaction.query.filter_by(user_id=current_user.id).all()
        form = TransactionUploadForm()
        add_account_form = AddAccountForm()
        existing_accounts = Account.query.filter_by(type='account').all()
        monthly_spending_by_category = [
            {"category": category.name, "amount": sum(transaction.amount for transaction in transactions if transaction.category_id == category.id)}
            for category in categories
            ]
    else:
        total_balance = 0
        monthly_spending_by_category = {}
        form = None
        add_account_form = None
        existing_accounts = None
    return render_template('index.html', total_balance=total_balance, monthly_spending_by_category=monthly_spending_by_category, form=form, add_account_form=add_account_form, existing_accounts=existing_accounts)


@app.route("/transactions/import", methods=["GET", "POST"])
def import_transactions():
    if current_user.is_authenticated:
        total_balance = current_user.total_balance
        categories = Category.query.filter_by(user_id=current_user.id).all()
        transactions = Transaction.query.filter_by(user_id=current_user.id).all()
        monthly_spending_by_category = [
            {"category": category.name, "amount": sum(transaction.amount for transaction in transactions if transaction.category_id == category.id)}
            for category in categories
            ]
    else:
        total_balance = 0
        monthly_spending_by_category = {}
    form = TransactionUploadForm()
    add_account_form = AddAccountForm()
    existing_accounts = Account.query.filter_by(type='account').all()
    if form.validate_on_submit():
        file = form.file.data
        account_id = form.account.data
        parse_transactions(file, account_id)
        flash("Transactions imported successfully!", "success")
        return redirect(url_for("index"))
    return render_template('base.html', total_balance=total_balance, monthly_spending_by_category=monthly_spending_by_category, form=form, add_account_form=add_account_form, existing_accounts=existing_accounts)

@app.route("/add_account", methods=["POST"])
def add_account():
    form = AddAccountForm()
    if form.validate_on_submit():
        account_name = form.account_name.data
        new_account = Account(type="account", name=account_name)
        db.session.add(new_account)
        db.session.commit()
        flash("Account added successfully!", "success")
    return redirect(url_for("import_transactions"))

@app.route("/add_category", methods=["POST"])
def add_category():
    form = AddCategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.category_name.data, user_id=current_user.id)
        db.session.add(category)
        db.session.add(category)
        db.session.commit()
        flash("Category added successfully!", "success")
    return redirect(url_for("transactions"))

@app.route("/transactions")
def transactions():
    add_category_form = AddCategoryForm()
    user_id = current_user.id
    page = request.args.get('page', 1, type=int)
    per_page = 50
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc()).paginate(page=page, per_page=per_page)
    categories = Category.query.all()
    return render_template("transactions.html", add_category_form=add_category_form, categories=categories, transactions=transactions)

@app.route('/transactions/update_category', methods=['POST'])
@login_required
def update_category():
    transaction_id = request.form.get('transaction_id')
    category_id = request.form.get('category_id')

    transaction = Transaction.query.get(transaction_id)
    category = Category.query.get(category_id) if category_id else None

    if transaction:
        transaction.category = category
        db.session.commit()
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error'})

@app.route('/delete_all_transactions', methods=['GET', 'POST'])
def delete_all_transactions():
    user_id = current_user.id
    Transaction.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return redirect(url_for('transactions'))

@app.route('/delete_transaction/<int:transaction_id>', methods=['GET', 'POST'])
def delete_transaction(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    if transaction and transaction.user_id == current_user.id:
        db.session.delete(transaction)
        db.session.commit()
    return redirect(url_for('transactions'))


@app.route("/authorize")
def authorize():
    # Implement OAuth2 authorization functionality
    pass

@app.route('/api/transactions')
@login_required
def api_transactions():
    transactions = current_user.transactions
    return jsonify([{
        'date': transaction.date.isoformat(),
        'amount': transaction.amount,
        'description': transaction.description,
        'account': transaction.account,
        'category': transaction.category,
    } for transaction in transactions])

@login_manager.user_loader
def load_user(user_id):
    return FinUser.query.get(int(user_id))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

if __name__ == "__main__":
    app.run(debug=True)
