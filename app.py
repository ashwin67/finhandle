from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import current_user, LoginManager
from flask_login import login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, extract
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finhandle.db'  # Use the appropriate database URI for your setup
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)  # Generate a random key for secure sessions

db = SQLAlchemy()
db.init_app(app)

from models.fin_user import FinUser
from models.transaction import Transaction

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Google OAuth2 client ID and secret
GOOGLE_CLIENT_ID = "your_google_client_id_here"
GOOGLE_CLIENT_SECRET = "your_google_client_secret_here"
GOOGLE_DISCOVERY_DOC = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

from views.forms import TransactionUploadForm
from views.auth import auth
from views.import_transactions import parse_transactions
app.register_blueprint(auth, url_prefix='/auth')


@app.route('/')
def index():
    if current_user.is_authenticated:
        total_balance = current_user.total_balance
        monthly_spending_by_category = current_user.get_monthly_spending_by_category()
    else:
        total_balance = 0
        monthly_spending_by_category = {}
    return render_template('index.html', total_balance=total_balance, monthly_spending_by_category=monthly_spending_by_category)


# Add more routes here for your views (e.g., stocks, assets, summary)

@app.route("/transactions/import", methods=["GET", "POST"])
def import_transactions():
    form = TransactionUploadForm()
    if form.validate_on_submit():
        file = form.file.data
        account_type = request.form.get('account_type')
        parse_transactions(file, account_type)
        flash("Transactions imported successfully!", "success")
        return redirect(url_for("index"))
    return render_template("import_transactions.html", form=form)

@app.route("/transactions")
def transactions():
    user_id = current_user.id
    page = request.args.get('page', 1, type=int)
    per_page = 50
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc()).paginate(page=page, per_page=per_page)
    return render_template("transactions.html", transactions=transactions)

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
