from app import db
from app import app  # Import the app object from the app package
from models.fin_user import FinUser  # Import all necessary models here
from models.transaction import Transaction
from sqlalchemy import MetaData
import os

def delete_existing_database():
    db_file = 'finhandle.db'  # Your database filename
    if os.path.exists(db_file):
        os.remove(db_file)
        print("Existing database file deleted.")
    else:
        print("No existing database file found.")

# init_db.py
def create_tables():
    with app.app_context():
        db.create_all()
        print("Database tables created.")

        meta = MetaData()
        meta.reflect(bind=db.engine)
        print("Existing tables:", meta.tables.keys())  # Print the list of table names in the database


if __name__ == '__main__':
    delete_existing_database()
    with app.app_context():
        create_tables()
