import pandas as pd
from flask_login import current_user
from datetime import datetime

from models.transaction import Transaction
from app import db

def parse_transactions(file):
    # Read the file using pandas
    df = pd.read_csv(file)

    # Clean and format the data
    # This step depends on the structure of your transaction file

    # Save the parsed transactions to the database
    for index, row in df.iterrows():
        date_format = "%d.%m.%Y"
        date_object = datetime.strptime(row["date"], date_format).date()
        transaction = Transaction(
            date=date_object,
            description=row["description"],
            amount=row["amount"],
            category=row["category"]
        )
        # Add the user ID to the transaction
        transaction.user_id = current_user.id

        db.session.add(transaction)
    db.session.commit()

