# views/main.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from views.forms import TransactionUploadForm, AddAccountForm, AddCategoryForm, CustomMappingForm
from views.import_transactions import parse_transactions
from models.parameters import Account, Category
from models.transaction import Transaction
from views.utilities import get_monthly_spending_by_category, get_base_template_data, get_income_this_month, get_expenses_this_month
from app import db

main = Blueprint('main', __name__)

@main.route('/')
def index():

    base_data = get_base_template_data()
    if current_user.is_authenticated:
        transactions = Transaction.query.filter_by(user_id=current_user.id).all()
        income_this_month = get_income_this_month(transactions)
        expenses_this_month = get_expenses_this_month(transactions)
        monthly_spending_by_category = get_monthly_spending_by_category(base_data['existing_categories'], transactions)
    else:
        income_this_month = 0
        expenses_this_month = 0
        monthly_spending_by_category = {}
    return render_template('index.html', 
        monthly_spending_by_category=monthly_spending_by_category,
        income_this_month=income_this_month,
        expenses_this_month=expenses_this_month,
        **base_data)


@main.route("/transactions")
def transactions():
    base_data = get_base_template_data()
    user_id = current_user.id
    page = request.args.get('page', 1, type=int)
    per_page = 50
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc()).paginate(page=page, per_page=per_page)
    return render_template("transactions.html", transactions=transactions, **base_data)

@main.route("/transactions/import", methods=["GET", "POST"])
def import_transactions():
    base_data = get_base_template_data()
    if current_user.is_authenticated:
        transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    form = TransactionUploadForm()
    if form.validate_on_submit():
        file = form.file.data
        account_id = form.account.data
        import pdb; pdb.set_trace()
        mapping_key = form.mapping_key.data
        custom_mapping = None
        if mapping_key != 'default':
            custom_mapping = current_user.custom_mappings[int(mapping_key)]
        parse_transactions(file, account_id, custom_mapping)
        flash("Transactions imported successfully!", "success")
        return redirect(url_for("main.index"))
    return render_template('base.html', **base_data)

@main.route("/add_account", methods=["POST"])
def add_account():
    form = AddAccountForm()
    if form.validate_on_submit():
        account_name = form.account_name.data
        new_account = Account(type="account", name=account_name)
        db.session.add(new_account)
        db.session.commit()
        flash("Account added successfully!", "success")
    return redirect(url_for("main.index"))

@main.route("/add_category", methods=["POST"])
def add_category():
    form = AddCategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.category_name.data, user_id=current_user.id)
        db.session.add(category)
        db.session.add(category)
        db.session.commit()
        flash("Category added successfully!", "success")
    return redirect(url_for("main.index"))

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

@main.route('/add_custom_mapping', methods=['POST'])
@login_required
def add_custom_mapping():
    form = CustomMappingForm()
    if form.validate_on_submit():
        new_mapping = {
            'mapping_name': form.mapping_name.data,
            'date': form.date.data,
            'description': form.description.data,
            'amount': form.amount.data
        }
        if current_user.custom_mappings is None:
            current_user.custom_mappings = [new_mapping]
        else:
            current_user.custom_mappings.append(new_mapping)

        db.session.commit()
        flash("Custom mapping added successfully.", "success")
    else:
        flash("Error: Please fill in all fields correctly.", "danger")
    return redirect(url_for('main.index'))
