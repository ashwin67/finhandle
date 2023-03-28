from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os


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

from views.auth import auth
from views.main import main

app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(main)

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
