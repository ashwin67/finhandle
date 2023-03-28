# views/main.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from views.forms import TransactionUploadForm, AddAccountForm, AddCategoryForm
from views.import_transactions import parse_transactions
from models.parameters import Account, Category
from models.transaction import Transaction
from utilities import get_monthly_spending_by_category
from app import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        total_balance = current_user.total_balance
        categories = Category.query.filter_by(user_id=current_user.id).all()
        transactions = Transaction.query.filter_by(user_id=current_user.id).all()
        form = TransactionUploadForm()
        add_account_form = AddAccountForm()
        existing_accounts = Account.query.filter_by(type='account').all()
        monthly_spending_by_category = get_monthly_spending_by_category(categories, transactions)
    else:
        total_balance = 0
        monthly_spending_by_category = {}
        form = None
        add_account_form = None
        existing_accounts = None
    return render_template('index.html', total_balance=total_balance, monthly_spending_by_category=monthly_spending_by_category, form=form, add_account_form=add_account_form, existing_accounts=existing_accounts)


@main.route("/transactions/import", methods=["GET", "POST"])
def import_transactions():
    if current_user.is_authenticated:
        total_balance = current_user.total_balance
        categories = Category.query.filter_by(user_id=current_user.id).all()
        transactions = Transaction.query.filter_by(user_id=current_user.id).all()
        monthly_spending_by_category = get_monthly_spending_by_category(categories, transactions)
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
        return redirect(url_for("main.index"))
    return render_template('base.html', total_balance=total_balance, monthly_spending_by_category=monthly_spending_by_category, form=form, add_account_form=add_account_form, existing_accounts=existing_accounts)

@main.route("/add_account", methods=["POST"])
def add_account():
    form = AddAccountForm()
    if form.validate_on_submit():
        account_name = form.account_name.data
        new_account = Account(type="account", name=account_name)
        db.session.add(new_account)
        db.session.commit()
        flash("Account added successfully!", "success")
    return redirect(url_for("main.import_transactions"))

@main.route("/add_category", methods=["POST"])
def add_category():
    form = AddCategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.category_name.data, user_id=current_user.id)
        db.session.add(category)
        db.session.add(category)
        db.session.commit()
        flash("Category added successfully!", "success")
    return redirect(url_for("main.transactions"))

@main.route("/transactions")
def transactions():
    add_category_form = AddCategoryForm()
    user_id = current_user.id
    page = request.args.get('page', 1, type=int)
    per_page = 50
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc()).paginate(page=page, per_page=per_page)
    categories = Category.query.all()
    return render_template("transactions.html", add_category_form=add_category_form, categories=categories, transactions=transactions)

@main.route('/transactions/update_category', methods=['POST'])
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

@main.route('/delete_all_transactions', methods=['GET', 'POST'])
def delete_all_transactions():
    user_id = current_user.id
    Transaction.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return redirect(url_for('main.transactions'))

@main.route('/delete_transaction/<int:transaction_id>', methods=['GET', 'POST'])
def delete_transaction(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    if transaction and transaction.user_id == current_user.id:
        db.session.delete(transaction)
        db.session.commit()
    return redirect(url_for('main.transactions'))


@main.route("/authorize")
def authorize():
    # Implement OAuth2 authorization functionality
    pass

@main.route('/api/transactions')
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