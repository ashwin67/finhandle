from flask import render_template
from flask_login import current_user
from views.forms import TransactionUploadForm, AddAccountForm, AddCategoryForm
from models.parameters import Account, Category
from models.transaction import Transaction

def get_monthly_spending_by_category(categories, transactions):
    return [
        {
            "category": category.name,
            "amount": sum(transaction.amount for transaction in transactions if transaction.category_id == category.id)
        }
        for category in categories
    ]

def get_base_template_data():
    data = {
        'add_category_form': None,
        'existing_categories': [],
        'add_account_form': None,
        'existing_accounts': None,
        'total_balance': 0,
        'transaction_form': None
    }

    if current_user.is_authenticated:
        data['add_category_form'] = AddCategoryForm()
        data['existing_categories'] = Category.query.filter_by(user_id=current_user.id).all()
        data['add_account_form'] = AddAccountForm()
        data['existing_accounts'] = Account.query.filter_by(type='account').all()
        data['total_balance'] = current_user.total_balance
        data['transaction_form'] = TransactionUploadForm()


    return data
