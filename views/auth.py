from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from models.fin_user import FinUser
from app import db

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the user already exists
        user = FinUser.query.filter_by(username=username).first()
        if user:
            return jsonify({'result': 'error', 'message': 'Username already exists. Please choose a different one.'})

        # Create a new user and save it to the database
        new_user = FinUser(username=username, email=email, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'result': 'success'})


@auth.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Find the user with the given username
        user = FinUser.query.filter_by(username=username).first()

        # Check if the user exists and the password is correct
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return jsonify({'result': 'success'})
        else:
            return jsonify({'result': 'error', 'message': 'Invalid username or password.'})


@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('index'))
